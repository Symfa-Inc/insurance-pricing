import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface ReportCardProps {
  title: string;
  markdown: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function resolveMarkdownImageSrc(src: string | undefined): string {
  if (!src) {
    return "";
  }

  if (
    src.startsWith("http://") ||
    src.startsWith("https://") ||
    src.startsWith("data:") ||
    src.startsWith("blob:")
  ) {
    return src;
  }

  if (src.startsWith("/api/")) {
    return `${API_BASE_URL}${src}`;
  }

  return src;
}

export function ReportCard({ title, markdown }: ReportCardProps) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <header>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Report</p>
        <h2 className="mt-2 text-2xl font-semibold text-slate-900">{title}</h2>
      </header>
      <div className="mt-6 space-y-4">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            p: ({ children }) => <p className="text-sm text-slate-600">{children}</p>,
            h1: ({ children }) => (
              <h1 className="pt-2 text-2xl font-semibold text-slate-900">{children}</h1>
            ),
            h2: ({ children }) => (
              <h2 className="pt-2 text-xl font-semibold text-slate-900">{children}</h2>
            ),
            h3: ({ children }) => (
              <h3 className="pt-2 text-lg font-semibold text-slate-900">{children}</h3>
            ),
            ul: ({ children }) => <ul className="list-disc pl-5 text-sm text-slate-600">{children}</ul>,
            ol: ({ children }) => <ol className="list-disc pl-5 text-sm text-slate-600">{children}</ol>,
            table: ({ children }) => (
              <div className="overflow-x-auto rounded-lg border border-slate-200">
                <table className="min-w-full border-collapse text-sm text-slate-600">{children}</table>
              </div>
            ),
            thead: ({ children }) => <thead className="bg-slate-50 text-slate-700">{children}</thead>,
            th: ({ children }) => (
              <th className="border border-slate-200 px-3 py-2 text-left font-semibold">{children}</th>
            ),
            td: ({ children }) => <td className="border border-slate-200 px-3 py-2 align-top">{children}</td>,
            img: ({ src, alt }) => (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={resolveMarkdownImageSrc(src)}
                alt={alt ?? ""}
                className="h-auto max-w-full rounded-lg border border-slate-100"
              />
            ),
          }}
        >
          {markdown}
        </ReactMarkdown>
      </div>
    </article>
  );
}
