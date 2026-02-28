import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { Login } from './pages/Auth/Login';
import { Register } from './pages/Auth/Register';
import { AuthCallback } from './pages/Auth/Callback';
import { DebugAuth } from './pages/Auth/DebugAuth';
import { LandingPage } from './pages/Landing/LandingPage';
import { ProjectList } from './pages/Projects/ProjectList';
import { NewProject } from './pages/Projects/NewProject';
import { ProjectDetail } from './pages/Projects/ProjectDetail';
import { ScriptEditor } from './pages/Script/ScriptEditor';
import { CharacterList } from './pages/Characters/CharacterList';
import { CharacterUpload } from './pages/Characters/CharacterUpload';
import { CharacterDetail } from './pages/Characters/CharacterDetail';
import { StoryboardEditor } from './pages/Storyboard/StoryboardEditor';
import { StoryboardCreate } from './pages/Storyboard/StoryboardCreate';
import { WorkflowPage } from './pages/Workflow/WorkflowPage';
import { ExportPage } from './pages/Export/ExportPage';
import { PaymentPage } from './pages/Payment/PaymentPage';
import { PaymentSuccess } from './pages/Payment/PaymentSuccess';
import { Layout } from './components/layout/Layout';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="/debug-auth" element={<DebugAuth />} />
          
          {/* All Routes with Layout */}
          <Route element={<Layout />}>
            <Route path="/" element={<LandingPage />} />
            <Route path="/projects" element={<ProjectList />} />
            <Route path="/projects/new" element={<NewProject />} />
            <Route path="/projects/:id" element={<ProjectDetail />} />
            <Route path="/projects/:projectId/script" element={<ScriptEditor />} />
            
            {/* Characters */}
            <Route path="/characters" element={<CharacterList />} />
            <Route path="/characters/new" element={<CharacterUpload />} />
            <Route path="/characters/:id" element={<CharacterDetail />} />
            
            {/* Storyboard */}
            <Route path="/storyboard/:projectId" element={<StoryboardEditor />} />
            <Route path="/storyboard/new" element={<StoryboardCreate />} />
            
            {/* Workflow */}
            <Route path="/workflow/:projectId" element={<WorkflowPage />} />
            
            {/* Export */}
            <Route path="/export/:projectId" element={<ExportPage />} />
            
            {/* Payment */}
            <Route path="/payment" element={<PaymentPage />} />
            <Route path="/payment/success" element={<PaymentSuccess />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
