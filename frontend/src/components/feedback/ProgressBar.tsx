interface ProgressBarProps {
  percentage: number;
  status: string;
  description?: string;
  showPercentage?: boolean;
}

export function ProgressBar({
  percentage,
  status,
  description,
  showPercentage = true,
}: ProgressBarProps) {
  const clampedPercentage = Math.min(100, Math.max(0, percentage));

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-gray-700">
          {description || '处理中...'}
        </span>
        {showPercentage && (
          <span className="text-sm text-gray-600 font-medium">
            {clampedPercentage.toFixed(0)}%
          </span>
        )}
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${clampedPercentage}%` }}
        />
      </div>
      {status && (
        <div className="mt-2 text-xs text-gray-500">{status}</div>
      )}
    </div>
  );
}
