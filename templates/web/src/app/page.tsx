export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-2xl text-center space-y-6">
        <h1 className="text-4xl font-bold tracking-tight">
          Welcome to Luymas App
        </h1>
        <p className="text-lg text-muted-foreground">
          Built with Luymas AI — Next.js + TypeScript + Tailwind CSS
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/api/health"
            className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition"
          >
            Health Check
          </a>
          <a
            href="https://github.com/your-org/luymas-ai"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 border border-border rounded-lg hover:bg-accent transition"
          >
            Documentation
          </a>
        </div>
      </div>
    </main>
  );
}
