import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { exportApi } from '../../api/export';
import { projectsApi } from '../../api/projects';
import type { Project } from '../../types';
import { ProgressBar } from '../../components/feedback/ProgressBar';
import { useWebSocket } from '../../hooks/useWebSocket';