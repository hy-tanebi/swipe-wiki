import { useEffect, useState } from "react";
import { fetchWiki, type WikiArticle } from "./api";

function WikiScreen() {
  const [articles, setArticles] = useState<WikiArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);

  const load = () => {
    setLoading(true);
    setLoadError(false);
    fetchWiki()
      .then((data) => setArticles(data))
      .catch(() => setLoadError(true))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <>
      <p className="count">保存済み {articles.length}件</p>

      {loading && <p className="status">読み込んでいます…</p>}
      {!loading && loadError && (
        <div className="status">
          <p>取得に失敗しました。再読み込みしてください。</p>
          <button type="button" onClick={load}>
            再読み込み
          </button>
        </div>
      )}
      {!loading && !loadError && articles.length === 0 && (
        <p className="status">保存した記事はまだありません。</p>
      )}

      <ul className="wiki-list">
        {articles.map((article) => (
          <li key={article.id} className="wiki-item">
            <a href={article.url} target="_blank" rel="noopener noreferrer">
              {article.title}
            </a>
            <p className="wiki-meta">
              保存日: {article.saved_at.slice(0, 10).replaceAll("-", "/")} ・{" "}
              {article.source}
            </p>
            {article.tags && (
              <p className="wiki-tags">{article.tags.split(",").join(" / ")}</p>
            )}
          </li>
        ))}
      </ul>
    </>
  );
}

export default WikiScreen;
