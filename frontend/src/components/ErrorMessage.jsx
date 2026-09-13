export function getErrorMessage(error) {
  if (error?.response?.data?.detail) return error.response.data.detail;
  if (error?.message) return error.message;
  return "Something went wrong. Please try again.";
}

export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="max-w-2xl mx-auto text-center py-12">
      <p className="text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3 text-sm">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 bg-surface hover:bg-white/10 px-4 py-2 rounded-full text-sm font-semibold transition-colors"
        >
          Try again
        </button>
      )}
    </div>
  );
}