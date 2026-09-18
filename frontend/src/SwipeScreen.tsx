import { useEffect, useState } from "react";
import {
  ApiError,
  createSwipe,
  fetchArticles,
  type Article,
  type Decision,
} from "./api";

const SWIPE_THRESHOLD = 100;

function SwipeScreen() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const [sending, setSending] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [dragX, setDragX] = useState(0);
  const [startX, setStartX] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    setLoadError(false);
    fetchArticles()
      .then((data) => setArticles(data))
      .catch(() => setLoadError(true))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const current = articles[0];

  const handlePointerDown = (e: React.PointerEvent<HTMLElement>) => {
    if (sending) return;
    setStartX(e.clientX);
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLElement>) => {
    if (startX === null) return;
    setDragX(e.clientX - startX);
  };

  const handlePointerUp = async () => {
    if (startX === null || !current) return;
    setStartX(null);

    let decision: Decision | null = null;
    if (dragX > SWIPE_THRESHOLD) decision = "keep";
    if (dragX < -SWIPE_THRESHOLD) decision = "drop";
    setDragX(0);
    if (!decision) return;

    setSending(true);
    setMessage(null);
    try {
      await createSwipe(current.id, decision);
      setArticles((prev) => prev.slice(1));
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setArticles((prev) => prev.slice(1));
        setMessage("この記事は判定済みだったので、次の記事に進みました。");
      } else {
        setMessage("保存に失敗しました。もう一度スワイプしてください。");
      }
    } finally {
      setSending(false);
    }
  };

  return (
    <>
      <p className="count">未判定 {articles.length}件</p>

      {message && <p className="message">{message}</p>}

      {loading && <p className="status">記事を読み込んでいます…</p>}
      {!loading && loadError && (
        <div className="status">
          <p>取得に失敗しました。再読み込みしてください。</p>
          <button type="button" onClick={load}>
            再読み込み
          </button>
        </div>
      )}
      {!loading && !loadError && !current && (
        <p className="status">未判定の記事はありません。</p>
      )}
      {current && (
        <ArticleCard
          article={current}
          dragX={dragX}
          sending={sending}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
        />
      )}

      {current && (
        <p className="help">← 左にスワイプで捨てる ／ 右にスワイプで残す →</p>
      )}
    </>
  );
}

type ArticleCardProps = {
  article: Article;
  dragX: number;
  sending: boolean;
  onPointerDown: (e: React.PointerEvent<HTMLElement>) => void;
  onPointerMove: (e: React.PointerEvent<HTMLElement>) => void;
  onPointerUp: () => void;
};

function ArticleCard({
  article,
  dragX,
  sending,
  onPointerDown,
  onPointerMove,
  onPointerUp,
}: ArticleCardProps) {
  const tags = article.tags ? article.tags.split(",") : [];
  const published = article.published_at.slice(0, 10).replaceAll("-", "/");

  return (
    <article
      className={`card${sending ? " sending" : ""}`}
      style={{
        transform: `translateX(${dragX}px) rotate(${dragX / 20}deg)`,
        transition: dragX === 0 ? "transform 0.2s" : "none",
      }}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerUp}
    >
      {dragX > SWIPE_THRESHOLD && <span className="hint keep">残す</span>}
      {dragX < -SWIPE_THRESHOLD && <span className="hint drop">捨てる</span>}

      <span className="source">{article.source}</span>
      <h2 className="title">{article.title}</h2>
      <p className="published">公開日: {published}</p>
      <ul className="tags">
        {tags.map((tag) => (
          <li key={tag}>{tag}</li>
        ))}
      </ul>

      {sending && <p className="sending-label">送信中…</p>}
    </article>
  );
}

export default SwipeScreen;
