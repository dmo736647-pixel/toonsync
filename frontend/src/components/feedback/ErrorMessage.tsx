import type { ErrorResponse } from '../../types';

interface ErrorMessageProps {
  error: ErrorResponse['error'];
  onDismiss?: () => void;
}

export function ErrorMessage({ error, onDismiss }: ErrorMessageProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center mb-2">
            <span className="text-red-600 text-xl mr-2">⚠️</span>
            <h3 className="text-red-800 font-semibold">{error.message}</h3>
          </div>
          
          <p className="text-red-600 text-sm mb-2">
            错误代码: {error.code} | 类别: {error.category}
          </p>

          {error.details && (
            <p className="text-red-700 text-sm mb-3">{error.details}</p>
          )}

          {error.solutions && error.solutions.length > 0 && (
            <div className="mt-4">
              <h4 className="text-red-800 font-medium mb-2">💡 解决方案：</h4>
              <div className="space-y-3">
                {error.solutions.map((solution, index) => (
                  <div key={index} className="bg-white rounded p-3">
                    <p className="text-red-800 font-medium mb-1">{solution.title}</p>
                    <p className="text-red-600 text-sm mb-2">{solution.description}</p>
                    {solution.steps && solution.steps.length > 0 && (
                      <ol className="list-decimal list-inside space-y-1 text-sm text-red-600">
                        {solution.steps.map((step, i) => (
                          <li key={i}>{step}</li>
                        ))}
                      </ol>
                    )}
                    {solution.documentation_url && (
                      <a
                        href={solution.documentation_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700 text-sm mt-2 inline-block"
                      >
                        查看文档 →
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-red-400 hover:text-red-600 ml-4 text-xl"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}
