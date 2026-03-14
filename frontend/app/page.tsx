"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import styles from "./page.module.css";

type StreamPayload = {
  final_report?: string;
  sub_topics?: string[];
  summaries?: Record<string, string>;
  contradictions?: string[];
  references?: string[];
};

type StreamEvent = {
  event: "node_complete" | "completed" | "error";
  node: string;
  current_step: string;
  payload: StreamPayload & { message?: string };
};

type HistoryCard = {
  id: string;
  query: string;
  timestamp: string;
};

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  state?: "streaming" | "complete";
  timestamp: string;
  steps?: string[];
};

const starterPrompts = [
  "Summarize the latest enterprise use cases for small language models.",
  "Compare quantum computing progress across academia and industry.",
  "Analyze the risks and opportunities of autonomous vehicles.",
];

const initialAssistantMessage =
  "Ask a research question and the system will plan, search, critique, and write a cited report.";

function slugToLabel(value: string) {
  return value
    .split("_")
    .map((item) => item.charAt(0).toUpperCase() + item.slice(1))
    .join(" ");
}

function formatTimestamp(date: Date) {
  return date.toLocaleTimeString([], {
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function Home() {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_BASE_URL ?? "http://localhost:8000";
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("Idle");
  const [isRunning, setIsRunning] = useState(false);
  const [steps, setSteps] = useState<string[]>([]);
  const [subTopics, setSubTopics] = useState<string[]>([]);
  const [contradictions, setContradictions] = useState<string[]>([]);
  const [references, setReferences] = useState<string[]>([]);
  const [finalReport, setFinalReport] = useState("");
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [activeView, setActiveView] = useState<"answer" | "process" | "sources">("answer");
  const [recentRuns, setRecentRuns] = useState<HistoryCard[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const answerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    return () => {
      eventSourceRef.current?.close();
    };
  }, []);

  useEffect(() => {
    answerRef.current?.scrollTo({
      top: answerRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  const timeline = useMemo(
    () =>
      steps.map((step, index) => ({
        id: `${step}-${index}`,
        title: slugToLabel(step),
        detail:
          step === "writer"
            ? "Compiled the final report and references."
            : `Completed the ${slugToLabel(step).toLowerCase()} agent.`,
      })),
    [steps],
  );

  function stopStream() {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
  }

  function resetRun() {
    setSteps([]);
    setSubTopics([]);
    setContradictions([]);
    setReferences([]);
    setFinalReport("");
    setError("");
    setCopied(false);
  }

  function newChat() {
    stopStream();
    resetRun();
    setQuery("");
    setStatus("Idle");
    setIsRunning(false);
    setActiveView("answer");
    setMessages([]);
    inputRef.current?.focus();
  }

  async function copyReport() {
    if (!finalReport) {
      return;
    }
    try {
      await navigator.clipboard.writeText(finalReport);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      setError("Copy failed. Your browser blocked clipboard access.");
    }
  }

  function jumpToAnswer() {
    answerRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    setActiveView("answer");
  }

  function startResearch(nextQuery: string) {
    if (!nextQuery.trim()) {
      return;
    }

    stopStream();
    resetRun();
    const normalizedQuery = nextQuery.trim();
    const timestamp = formatTimestamp(new Date());
    setQuery(normalizedQuery);
    setStatus("Connecting");
    setIsRunning(true);
    const runId = `${Date.now()}`;
    setMessages((current) => [
      ...current,
      {
        id: `${runId}-user`,
        role: "user",
        content: normalizedQuery,
        state: "complete",
        timestamp,
      },
      {
        id: `${runId}-assistant`,
        role: "assistant",
        content: "Research started. Planning, searching, and compiling the report.",
        state: "streaming",
        timestamp,
        steps: [],
      },
    ]);
    setRecentRuns((current) => {
      const nextItem: HistoryCard = {
        id: normalizedQuery.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, ""),
        query: normalizedQuery,
        timestamp,
      };
      return [nextItem, ...current.filter((item) => item.query !== normalizedQuery)].slice(0, 6);
    });

    const url = new URL("/research/stream", backendUrl);
    url.searchParams.set("query", normalizedQuery);
    const stream = new EventSource(url.toString());
    eventSourceRef.current = stream;

    stream.onopen = () => {
      setStatus("Running agents");
    };

    stream.onmessage = (message) => {
      const event = JSON.parse(message.data) as StreamEvent;
      const payload = event.payload ?? {};

      if (event.event === "node_complete") {
        setSteps((current) => {
          if (current[current.length - 1] === event.current_step) {
            return current;
          }
          return [...current, event.current_step];
        });
        setSubTopics(payload.sub_topics ?? []);
        setContradictions(payload.contradictions ?? []);
        setReferences(payload.references ?? []);
        setStatus(`Running ${slugToLabel(event.current_step)}`);
        setMessages((current) =>
          current.map((message) =>
            message.id === `${runId}-assistant`
              ? {
                  ...message,
                  content: `Working on ${slugToLabel(event.current_step).toLowerCase()}...`,
                  state: "streaming",
                  steps: [...new Set([...(message.steps ?? []), event.current_step])],
                }
              : message,
          ),
        );
      }

      if (event.event === "completed") {
        setSubTopics(payload.sub_topics ?? []);
        setContradictions(payload.contradictions ?? []);
        setReferences(payload.references ?? []);
        setFinalReport(payload.final_report ?? "");
        setStatus("Completed");
        setIsRunning(false);
        setActiveView("answer");
        setMessages((current) =>
          current.map((message) =>
            message.id === `${runId}-assistant`
              ? {
                  ...message,
                  content: payload.final_report ?? "Research completed.",
                  state: "complete",
                  steps: [...new Set([...(message.steps ?? []), "writer"])],
                }
              : message,
          ),
        );
        stopStream();
      }

      if (event.event === "error") {
        const messageText = payload.message ?? "The research run failed.";
        setError(messageText);
        setStatus("Failed");
        setIsRunning(false);
        setMessages((current) =>
          current.map((message) =>
            message.id === `${runId}-assistant`
              ? {
                  ...message,
                  content: messageText,
                  state: "complete",
                }
              : message,
          ),
        );
        stopStream();
      }
    };

    stream.onerror = () => {
      setError("The frontend could not read the backend event stream. Check that the API is running and CORS is open.");
      setStatus("Failed");
      setIsRunning(false);
      setMessages((current) =>
        current.map((message) =>
          message.id === `${runId}-assistant`
            ? {
                ...message,
                content: "The research run failed. Check the backend connection and try again.",
                state: "complete",
                steps: message.steps ?? [],
              }
            : message,
        ),
      );
      stopStream();
    };
  }

  return (
    <main className={styles.viewport}>
      <div
        className={`${styles.shell} ${leftCollapsed ? styles.shellLeftCollapsed : ""} ${
          rightCollapsed ? styles.shellRightCollapsed : ""
        }`}
      >
        <aside className={`${styles.sidebar} ${leftCollapsed ? styles.panelHidden : ""}`}>
          <button className={styles.backButton} aria-label="Start a new chat" onClick={newChat} type="button">
            +
          </button>
          <nav className={styles.iconRail}>
            <button
              className={`${styles.railButton} ${activeView === "answer" ? styles.railButtonActive : ""}`}
              onClick={() => setActiveView("answer")}
              type="button"
              title="Answer"
            >
              ◉
            </button>
            <button
              className={`${styles.railButton} ${activeView === "process" ? styles.railButtonActive : ""}`}
              onClick={() => setActiveView("process")}
              type="button"
              title="Process"
            >
              ≡
            </button>
            <button
              className={`${styles.railButton} ${activeView === "sources" ? styles.railButtonActive : ""}`}
              onClick={() => setActiveView("sources")}
              type="button"
              title="Sources"
            >
              ◫
            </button>
          </nav>
          <div className={styles.sidebarFooter}>
            <button className={styles.railButton} onClick={copyReport} type="button" title="Copy report">
              {copied ? "✓" : "⧉"}
            </button>
            <div className={styles.avatarSmall}>MK</div>
          </div>
        </aside>

        <section className={`${styles.resultsPanel} ${leftCollapsed ? styles.panelCollapsed : ""}`}>
          <header className={styles.panelHeader}>
            <div>
              <h1>Chat Results</h1>
              <p>Previous conversations from this session</p>
            </div>
            <button
              className={styles.panelToggle}
              onClick={() => setLeftCollapsed((current) => !current)}
              type="button"
            >
              {leftCollapsed ? "Show" : "Hide"}
            </button>
          </header>

          {!leftCollapsed ? (
            <div className={styles.historyList}>
              {recentRuns.length === 0 ? (
                <div className={styles.historyListCard}>
                  <p className={styles.cardEyebrow}>No conversations yet</p>
                  <span className={styles.cardMeta}>Start a chat to see it listed here.</span>
                </div>
              ) : (
                recentRuns.map((card, index) => (
                  <button
                    key={`${card.id}-${index}`}
                    className={`${styles.historyListCard} ${styles.historyButton}`}
                    onClick={() => startResearch(card.query)}
                    type="button"
                  >
                    <div className={styles.historyTop}>
                      <div>
                        <p className={styles.cardEyebrow}>{index === 0 ? "Latest run" : "Previous conversation"}</p>
                        <span className={styles.cardMeta}>{card.timestamp}</span>
                      </div>
                      <span className={styles.arrowBadge}>↗</span>
                    </div>
                    <div className={styles.searchSnippet}>
                      <span>{card.query}</span>
                    </div>
                  </button>
                ))
              )}
            </div>
          ) : null}
        </section>

        <section className={styles.chatPanel}>
          <div className={styles.chatHeader}>
            <div className={styles.chatHeaderTitle}>
              <button
                className={styles.inlineToggle}
                onClick={() => setLeftCollapsed((current) => !current)}
                type="button"
                title="Toggle chat results"
              >
                {leftCollapsed ? "»" : "«"}
              </button>
              <span className={styles.sparkle}>✦</span>
              <h2>New Chat</h2>
            </div>
            <div className={styles.headerActions}>
              <button className={styles.headerActionButton} onClick={jumpToAnswer} type="button">
                Answer
              </button>
              <button className={styles.closeButton} onClick={newChat} type="button">
                New
              </button>
            </div>
          </div>

          <div className={styles.workspace}>
            <div className={styles.mainColumn}>
              <div className={styles.conversation}>
                {messages.length === 0 ? (
                  <section className={styles.heroCard}>
                    <div>
                      <p className={styles.greeting}>Hi, Mohit!</p>
                      <h3>How can I help you?</h3>
                      <p className={styles.heroCopy}>{initialAssistantMessage}</p>
                    </div>
                  </section>
                ) : (
                  <div className={styles.chatThread} ref={answerRef}>
                    {messages.map((message) => (
                      <article
                        key={message.id}
                        className={`${styles.chatBubble} ${
                          message.role === "user" ? styles.userBubble : styles.assistantBubble
                        }`}
                      >
                        <div className={styles.bubbleMeta}>
                          <span>{message.role === "user" ? "You" : "AutoResearch"}</span>
                          <div className={styles.bubbleMetaRight}>
                            <span>{message.timestamp}</span>
                            {message.state === "streaming" ? <span className={styles.streamingDot}>Working</span> : null}
                          </div>
                        </div>
                        {message.role === "assistant" && message.state === "complete" ? (
                          <div className={styles.markdownBody}>
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                          </div>
                        ) : (
                          <p className={styles.bubbleText}>{message.content}</p>
                        )}
                        {message.role === "assistant" && (message.steps?.length ?? 0) > 0 ? (
                          <div className={styles.stepRow}>
                            {message.steps?.map((step) => (
                              <span key={`${message.id}-${step}`} className={styles.stepChip}>
                                {slugToLabel(step)}
                              </span>
                            ))}
                          </div>
                        ) : null}
                      </article>
                    ))}
                  </div>
                )}
              </div>

              <div className={styles.inputDock}>
                <div className={styles.promptSuggestions}>
                  {starterPrompts.map((prompt) => (
                    <button
                      key={prompt}
                      className={styles.promptChip}
                      onClick={() => startResearch(prompt)}
                      type="button"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>

                <div className={styles.inputRow}>
                  <textarea
                    ref={inputRef}
                    className={styles.input}
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder="Ask me anything ..."
                    rows={2}
                  />
                  <button
                    className={styles.sendButton}
                    onClick={() => startResearch(query)}
                    type="button"
                    disabled={isRunning}
                  >
                    ↑
                  </button>
                </div>
              </div>
            </div>

            <div className={`${styles.sideColumn} ${rightCollapsed ? styles.panelCollapsed : ""}`}>
              <section className={styles.statusPanel}>
                <div className={styles.sideHeader}>
                  {!rightCollapsed ? <h3>Workspace</h3> : null}
                  <button
                    className={`${styles.panelToggle} ${rightCollapsed ? styles.panelToggleCompact : ""}`}
                    onClick={() => setRightCollapsed((current) => !current)}
                    type="button"
                    title={rightCollapsed ? "Expand workspace" : "Collapse workspace"}
                  >
                    {rightCollapsed ? "«" : "Hide"}
                  </button>
                </div>
                {!rightCollapsed ? (
                  <>
                    <div className={styles.statusHeader}>
                      <div>
                        <p className={styles.statusEyebrow}>Run status</p>
                        <h4>{status}</h4>
                      </div>
                      <span className={isRunning ? styles.statusPillLive : styles.statusPillIdle}>
                        {isRunning ? "Streaming" : "Ready"}
                      </span>
                    </div>

                    {error ? <p className={styles.errorText}>{error}</p> : null}

                    <div className={styles.statusGrid}>
                      <div className={styles.metricCard}>
                        <span>Sub-topics</span>
                        <strong>{subTopics.length}</strong>
                      </div>
                      <div className={styles.metricCard}>
                        <span>Contradictions</span>
                        <strong>{contradictions.length}</strong>
                      </div>
                      <div className={styles.metricCard}>
                        <span>References</span>
                        <strong>{references.length}</strong>
                      </div>
                    </div>
                  </>
                ) : null}
              </section>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
