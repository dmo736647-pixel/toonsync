"""角色一致性API端点"""
import time
import tempfile
import os
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.character import Character
from app.schemas.character_consistency import (
    ConsistencyModelResponse,
    ConsistencyScoreResponse,
    GenerateFrameResponse,
    BatchGenerateResponse,
    ValidateConsistencyRequest
)
from app.services.character_consistency import (
    get_character_consistency_engine,
    ConsistencyModel
)

router = APIRouter(prefix="/character-consistency", tags=["character-consistency"])


@router.post("/extract-features", response_model=ConsistencyModelResponse)
async def extract_character_features(
    character_id: str = Form(...),
    reference_image: UploadFile = File(..., description="角色参考图像"),
    style: str = Form("anime"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    从参考图像提取角色特征，创建一致性模型
    
    参数:
        character_id: 角色ID
        reference_image: 上传的参考图像
        style: 渲染风格（anime或realistic）
        current_user: 当前用户
        db: 数据库会话
    
    返回:
        ConsistencyModelResponse: 一致性模型
    """
    # 验证文件类型
    if not reference_image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="文件必须是图像格式")
    
    # 验证风格参数
    if style not in ["anime", "realistic"]:
        raise HTTPException(status_code=400, detail="风格必须是anime或realistic")
    
    # 验证角色是否存在且属于当前用户
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        content = await reference_image.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # 获取角色一致性引擎
        engine = get_character_consistency_engine()
        
        # 提取特征
        consistency_model = engine.extract_character_features(
            reference_image_path=temp_file_path,
            character_id=character_id,
            style=style
        )
        
        # 保存一致性模型（实际应用中应保存到S3）
        model_path = f"/tmp/consistency_model_{character_id}.json"
        consistency_model.save(model_path)
        
        # 更新角色记录
        character.consistency_model_url = model_path
        db.commit()
        
        # 转换为响应格式
        return ConsistencyModelResponse(
            character_id=consistency_model.character_id,
            reference_image_path=consistency_model.reference_image_path,
            facial_features=consistency_model.facial_features,
            clothing_features=consistency_model.clothing_features,
            style=consistency_model.style,
            created_at=consistency_model.created_at.isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"特征提取失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@router.post("/generate-frame", response_model=GenerateFrameResponse)
async def generate_storyboard_frame(
    character_id: str = Form(...),
    scene_description: str = Form(...),
    style: str = Form("anime"),
    reference_image_url: Optional[str] = Form(None),
    pose_reference: Optional[UploadFile] = File(None, description="姿态参考图"),
    db: Session = Depends(get_db)
):
    """
    生成单个分镜图像
    
    参数:
        character_id: 角色ID
        scene_description: 场景描述
        style: 渲染风格
        pose_reference: 可选的姿态参考图
        current_user: 当前用户
        db: 数据库会话
    
    返回:
        GenerateFrameResponse: 生成的分镜图像信息
    """
    start_time = time.time()
    
    character = None
    if not reference_image_url:
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="角色不存在")

    try:
        if reference_image_url:
            consistency_model = ConsistencyModel(
                character_id=character_id,
                reference_image_path=reference_image_url,
                facial_features={},
                clothing_features={},
                style=style
            )
        else:
            if character.consistency_model_url and os.path.exists(character.consistency_model_url):
                consistency_model = ConsistencyModel.load(character.consistency_model_url)
            else:
                if not character.reference_image_url:
                    raise HTTPException(status_code=400, detail="角色没有参考图")

                consistency_model = ConsistencyModel(
                    character_id=character.id,
                    reference_image_path=character.reference_image_url,
                    facial_features={},
                    clothing_features={},
                    style=style
                )
        
        # 获取角色一致性引擎
        engine = get_character_consistency_engine()
        
        # 处理姿态参考图（如果有）
        pose_reference_path = None
        if pose_reference:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                content = await pose_reference.read()
                temp_file.write(content)
                pose_reference_path = temp_file.name
        
        # 生成分镜
        frame_path = engine.generate_storyboard_frame(
            consistency_model=consistency_model,
            scene_description=scene_description,
            pose_reference=pose_reference_path
        )
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        # 返回响应
        return GenerateFrameResponse(
            frame_url=frame_path,
            character_id=character_id,
            scene_description=scene_description,
            style=style,
            processing_time_seconds=processing_time
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"分镜生成失败: {str(e)}")
    
    finally:
        # 清理临时文件
        if pose_reference_path and os.path.exists(pose_reference_path):
            os.unlink(pose_reference_path)


@router.post("/validate-consistency", response_model=ConsistencyScoreResponse)
async def validate_consistency(
    request: ValidateConsistencyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    验证生成的分镜与参考图像的一致性
    
    参数:
        request: 验证请求
        current_user: 当前用户
        db: 数据库会话
    
    返回:
        ConsistencyScoreResponse: 一致性评分
    """
    # 验证角色是否存在
    character = db.query(Character).filter(Character.id == request.character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    try:
        # 获取角色一致性引擎
        engine = get_character_consistency_engine()
        
        # 验证一致性
        score = engine.validate_consistency(
            reference_image_path=character.reference_image_url,
            generated_frames=request.generated_frame_urls
        )
        
        # 返回响应
        return ConsistencyScoreResponse(
            facial_similarity=score.facial_similarity,
            clothing_consistency=score.clothing_consistency,
            overall_score=score.overall_score,
            meets_requirements=score.meets_requirements(),
            details=score.details
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"一致性验证失败: {str(e)}")


@router.post("/batch-generate", response_model=BatchGenerateResponse)
async def batch_generate_frames(
    character_id: str = Form(...),
    scene_descriptions: str = Form(..., description="场景描述列表（JSON数组字符串）"),
    style: str = Form("anime"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量生成分镜图像
    
    参数:
        character_id: 角色ID
        scene_descriptions: 场景描述列表（JSON格式）
        style: 渲染风格
        current_user: 当前用户
        db: 数据库会话
    
    返回:
        BatchGenerateResponse: 批量生成结果
    """
    import json
    
    start_time = time.time()
    
    # 解析场景描述列表
    try:
        descriptions = json.loads(scene_descriptions)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="场景描述必须是有效的JSON数组")
    
    # 验证角色是否存在
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 验证一致性模型是否存在
    if not character.consistency_model_url:
        raise HTTPException(status_code=400, detail="角色尚未创建一致性模型，请先提取特征")
    
    try:
        # 加载一致性模型
        consistency_model = ConsistencyModel.load(character.consistency_model_url)
        
        # 获取角色一致性引擎
        engine = get_character_consistency_engine()
        
        # 批量生成分镜
        output_dir = f"/tmp/frames_{character_id}"
        frame_paths = engine.batch_generate_frames(
            consistency_model=consistency_model,
            scene_descriptions=descriptions,
            output_dir=output_dir
        )
        
        # 验证一致性
        score = engine.validate_consistency(
            reference_image_path=character.reference_image_url,
            generated_frames=frame_paths
        )
        
        # 计算处理时间
        processing_time = time.time() - start_time
        
        # 返回响应
        return BatchGenerateResponse(
            frame_urls=frame_paths,
            character_id=character_id,
            total_frames=len(frame_paths),
            consistency_score=ConsistencyScoreResponse(
                facial_similarity=score.facial_similarity,
                clothing_consistency=score.clothing_consistency,
                overall_score=score.overall_score,
                meets_requirements=score.meets_requirements(),
                details=score.details
            ),
            processing_time_seconds=processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量生成失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    健康检查端点
    
    返回:
        dict: 服务状态
    """
    try:
        engine = get_character_consistency_engine()
        return {
            "status": "healthy",
            "supported_styles": engine.SUPPORTED_STYLES,
            "service": "character-consistency"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"服务不可用: {str(e)}")
