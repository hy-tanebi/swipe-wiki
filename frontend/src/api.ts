export type Article = {
  id: number
  title: string
  url: string
  tags: string | null
  published_at: string
  source: string
}

export type Decision = 'keep' | 'drop'

export type Swipe = {
  id: number
  article_id: number
  decision: Decision
  created_at: string
}

export type WikiArticle = {
  id: number
  title: string
  url: string
  tags: string | null
  published_at: string
  source: string
  saved_at: string
}

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init)
  if (!res.ok) {
    throw new ApiError(res.status, `${res.status} ${res.statusText}`)
  }
  return (await res.json()) as T
}

export function fetchArticles(): Promise<Article[]> {
  return request<Article[]>('/articles')
}

export function createSwipe(articleId: number, decision: Decision): Promise<Swipe> {
  return request<Swipe>('/swipes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ article_id: articleId, decision }),
  })
}

export function fetchWiki(): Promise<WikiArticle[]> {
  return request<WikiArticle[]>('/wiki')
}
