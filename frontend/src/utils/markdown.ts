import MarkdownIt from "markdown-it"
import hljs from "highlight.js"

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  highlight(str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang, ignoreIllegals: true }).value}</code></pre>`
      } catch {
        // fallthrough
      }
    }
    return `<pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>`
  },
})

export function renderMarkdown(text: string): string {
  // Collapse 3+ consecutive newlines into 1 (single line break, more compact)
  const normalized = text.replace(/\n{3,}/g, "\n")
  return md.render(normalized)
}
