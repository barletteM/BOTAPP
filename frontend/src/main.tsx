import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { ArrowLeft, Bot as BotIcon, FileText, Lock, MessageSquare, Upload, Users } from "lucide-react";
import { api } from "./api";
import type { Bot, ChatMessage, ChatSession, FAQ, KnowledgeDocument } from "./types";
import "./styles.css";

type View = "select" | "chat" | "login" | "admin";

function App() {
  const [bots, setBots] = useState<Bot[]>([]);
  const [selected, setSelected] = useState<Bot | null>(null);
  const [view, setView] = useState<View>("select");

  useEffect(() => {
    api.listBots().then(setBots).catch(() => setBots([]));
  }, []);

  const chooseBot = (bot: Bot, next: View) => {
    setSelected(bot);
    setView(next);
  };

  return (
    <main>
      <header className="topbar">
        <button className="brand" onClick={() => setView("select")}>
          <BotIcon size={22} /> Glowdom Reception
        </button>
        <button className="ghost" onClick={() => setView(localStorage.getItem("glowdom_token") ? "admin" : "login")}>
          <Lock size={18} /> Admin
        </button>
      </header>
      {view === "select" && <BotSelector bots={bots} onChat={(bot) => chooseBot(bot, "chat")} onManage={(bot) => chooseBot(bot, localStorage.getItem("glowdom_token") ? "admin" : "login")} />}
      {view === "chat" && selected && <ChatPage bot={selected} onBack={() => setView("select")} />}
      {view === "login" && <LoginPage onDone={() => setView("admin")} />}
      {view === "admin" && <AdminPage bots={bots} selected={selected ?? bots[0] ?? null} onSelect={setSelected} />}
    </main>
  );
}

function BotSelector({ bots, onChat, onManage }: { bots: Bot[]; onChat: (bot: Bot) => void; onManage: (bot: Bot) => void }) {
  return (
    <section className="selector">
      <div>
        <p className="eyebrow">Multi-bot inquiry desk</p>
        <h1>Choose the reception assistant you need.</h1>
      </div>
      <div className="bot-grid">
        {bots.map((bot) => (
          <article className="bot-card" key={bot.id}>
            <BotIcon />
            <h2>{bot.name}</h2>
            <p>{bot.description}</p>
            <div className="row">
              <button onClick={() => onChat(bot)}><MessageSquare size={18} /> Chat</button>
              <button className="secondary" onClick={() => onManage(bot)}><FileText size={18} /> Manage</button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function ChatPage({ bot, onBack }: { bot: Bot; onBack: () => void }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [message, setMessage] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function send() {
    if (!message.trim() || busy) return;
    const outgoing: ChatMessage = { id: crypto.randomUUID(), role: "user", content: message, created_at: new Date().toISOString() };
    setMessages((items) => [...items, outgoing]);
    setMessage("");
    setBusy(true);
    try {
      const response = await api.chat(bot.slug, outgoing.content, sessionId);
      setSessionId(response.session_id);
      setMessages((items) => [...items, { id: crypto.randomUUID(), role: "assistant", content: response.answer, created_at: new Date().toISOString() }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="chat-layout">
      <aside className="info-panel">
        <button className="ghost" onClick={onBack}><ArrowLeft size={18} /> Back</button>
        <h1>{bot.name}</h1>
        <p>{bot.description}</p>
        <dl>
          <dt>Hours</dt><dd>{bot.office_hours || "Ask the assistant or contact the office."}</dd>
          <dt>Location</dt><dd>{bot.location || "Contact the office for directions."}</dd>
          <dt>Contact</dt><dd>{bot.phone || bot.email || "Not yet configured"}</dd>
        </dl>
      </aside>
      <section className="chat-panel">
        <div className="messages">
          {messages.length === 0 && <p className="empty">Ask about services, applications, documents, fees, appointments, office hours, or directions.</p>}
          {messages.map((item) => <div className={`bubble ${item.role}`} key={item.id}>{item.content}</div>)}
          {busy && <div className="bubble assistant">Checking approved information...</div>}
        </div>
        <div className="composer">
          <input value={message} onChange={(event) => setMessage(event.target.value)} onKeyDown={(event) => event.key === "Enter" && send()} placeholder="Type your question" />
          <button onClick={send}>Send</button>
        </div>
      </section>
    </section>
  );
}

function LoginPage({ onDone }: { onDone: () => void }) {
  const [email, setEmail] = useState("admin@glowdom.local");
  const [password, setPassword] = useState("ChangeMe123!");
  const [error, setError] = useState("");
  async function login() {
    try {
      const result = await api.login(email, password);
      localStorage.setItem("glowdom_token", result.access_token);
      onDone();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }
  return (
    <section className="login">
      <h1>Admin login</h1>
      <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" />
      <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Password" />
      {error && <p className="error">{error}</p>}
      <button onClick={login}>Login</button>
    </section>
  );
}

function AdminPage({ bots, selected, onSelect }: { bots: Bot[]; selected: Bot | null; onSelect: (bot: Bot) => void }) {
  const [tab, setTab] = useState<"profile" | "knowledge" | "faqs" | "history">("profile");
  if (!selected) return <section className="selector"><p>No bots available.</p></section>;
  return (
    <section className="admin-layout">
      <aside className="admin-nav">
        <h1>Dashboard</h1>
        {bots.map((bot) => <button className={bot.id === selected.id ? "active" : ""} onClick={() => onSelect(bot)} key={bot.id}><Users size={17} /> {bot.name}</button>)}
      </aside>
      <section className="admin-main">
        <div className="tabs">
          {(["profile", "knowledge", "faqs", "history"] as const).map((item) => <button className={tab === item ? "active" : ""} onClick={() => setTab(item)} key={item}>{item}</button>)}
        </div>
        {tab === "profile" && <ProfileManager bot={selected} />}
        {tab === "knowledge" && <KnowledgeManager bot={selected} />}
        {tab === "faqs" && <FaqManager bot={selected} />}
        {tab === "history" && <History bot={selected} />}
      </section>
    </section>
  );
}

function ProfileManager({ bot }: { bot: Bot }) {
  const [form, setForm] = useState(bot);
  useEffect(() => setForm(bot), [bot]);
  return (
    <div className="stack">
      {(["office_hours", "location", "phone", "email", "website", "reception_instructions"] as const).map((field) => (
        <label key={field}>{field.replaceAll("_", " ")}
          <textarea value={form[field]} onChange={(event) => setForm({ ...form, [field]: event.target.value })} />
        </label>
      ))}
      <button onClick={() => api.updateBot(bot.slug, form).then(setForm)}>Save profile</button>
    </div>
  );
}

function KnowledgeManager({ bot }: { bot: Bot }) {
  const [docs, setDocs] = useState<KnowledgeDocument[]>([]);
  const [documentId, setDocumentId] = useState("");
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [note, setNote] = useState("New approved information");
  useEffect(() => { api.listDocuments(bot.slug).then(setDocs); }, [bot]);
  async function paste() {
    const doc = documentId
      ? await api.addDocumentVersion(bot.slug, documentId, title || "Updated document", text, note)
      : await api.pasteKnowledge(bot.slug, title, text, note);
    setDocs([doc, ...docs.filter((item) => item.id !== doc.id)]);
    setDocumentId("");
    setTitle("");
    setText("");
  }
  async function upload(file: File | undefined) {
    if (!file) return;
    const doc = await api.uploadKnowledge(bot.slug, file, note);
    setDocs([doc, ...docs]);
  }
  return (
    <div className="two-col">
      <div className="stack">
        <label>Upload PDF, DOCX, TXT, or CSV<input type="file" accept=".pdf,.docx,.txt,.csv" onChange={(event) => upload(event.target.files?.[0])} /></label>
        <label>Change note<input value={note} onChange={(event) => setNote(event.target.value)} /></label>
        <label>Update existing document
          <select value={documentId} onChange={(event) => setDocumentId(event.target.value)}>
            <option value="">Create new knowledge document</option>
            {docs.map((doc) => <option value={doc.id} key={doc.id}>{doc.title}</option>)}
          </select>
        </label>
        <label>Manual/website text title<input value={title} onChange={(event) => setTitle(event.target.value)} /></label>
        <label>Approved text<textarea className="tall" value={text} onChange={(event) => setText(event.target.value)} /></label>
        <button onClick={paste}><Upload size={18} /> Add text</button>
      </div>
      <List title="Knowledge documents" items={docs.map((doc) => `${doc.title} | ${doc.source_type} | v${doc.current_version}`)} />
    </div>
  );
}

function FaqManager({ bot }: { bot: Bot }) {
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  useEffect(() => { api.listFaqs(bot.slug).then(setFaqs); }, [bot]);
  async function add() {
    const faq = await api.createFaq(bot.slug, question, answer);
    setFaqs([faq, ...faqs]);
    setQuestion("");
    setAnswer("");
  }
  return (
    <div className="two-col">
      <div className="stack">
        <label>Question<textarea value={question} onChange={(event) => setQuestion(event.target.value)} /></label>
        <label>Answer<textarea value={answer} onChange={(event) => setAnswer(event.target.value)} /></label>
        <button onClick={add}>Add FAQ</button>
      </div>
      <div className="list"><h2>FAQs</h2>{faqs.map((faq) => <article key={faq.id}><strong>{faq.question}</strong><p>{faq.answer}</p></article>)}</div>
    </div>
  );
}

function History({ bot }: { bot: Bot }) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  useEffect(() => { api.chatHistory(bot.slug).then(setSessions); }, [bot]);
  return <div className="list"><h2>Chat history</h2>{sessions.map((session) => <article key={session.id}>{session.messages.map((msg) => <p key={msg.id}><strong>{msg.role}:</strong> {msg.content}</p>)}</article>)}</div>;
}

function List({ title, items }: { title: string; items: string[] }) {
  return <div className="list"><h2>{title}</h2>{items.map((item) => <article key={item}>{item}</article>)}</div>;
}

createRoot(document.getElementById("root")!).render(<App />);
