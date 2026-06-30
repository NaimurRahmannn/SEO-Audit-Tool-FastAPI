export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col items-center justify-center gap-8 px-4">
      <h1 className="text-4xl font-bold tracking-tight">SEO Audit Tool</h1>

      <form className="flex w-full flex-col gap-3 sm:flex-row">
        <input
          type="url"
          name="url"
          placeholder="https://example.com"
          aria-label="URL to audit"
          className="flex-1 rounded-md border border-gray-300 px-4 py-2 shadow-sm focus:border-gray-500 focus:outline-none"
        />
        <button
          type="submit"
          className="rounded-md bg-gray-900 px-5 py-2 font-medium text-white hover:bg-gray-700"
        >
          Audit
        </button>
      </form>
    </main>
  );
}
