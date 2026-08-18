export default function LoadingSpinner() {
  return (
    <div className="flex justify-center items-center py-20">
      <div className="w-10 h-10 border-2 border-white/10 border-t-accent rounded-full animate-spin" />
    </div>
  );
}
