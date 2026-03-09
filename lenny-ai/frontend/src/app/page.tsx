"use client"

import { useState, useRef, useEffect } from "react"
import ReactMarkdown from "react-markdown"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Send, User, Sparkles, Loader2 } from "lucide-react"

type Source = {
  guest: string
  title: string
  source: string
  content_snippet: string
}

type Message = {
  id: string
  role: "user" | "assistant"
  content: string
  sources?: Source[]
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hi! I'm PM Buddy, your AI Product Manager Assistant. Ask me anything about product strategy, growth, or startups!"
    }
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMsg: Message = { id: Date.now().toString(), role: "user", content: input }
    setMessages(prev => [...prev, userMsg])
    setInput("")
    setIsLoading(true)

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMsg.content })
      })

      if (!res.ok) throw new Error("Failed to fetch response")

      const data = await res.json()

      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.reply,
        sources: data.sources
      }

      setMessages(prev => [...prev, aiMsg])
    } catch (error) {
      console.error(error)
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I ran into an error connecting to my brain. Make sure the backend server is running."
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-slate-50 text-slate-900 p-4 md:p-8 max-w-4xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2 text-blue-700">
            <Sparkles className="w-6 h-6 text-blue-600" /> PM Buddy
          </h1>
          <p className="text-slate-500 text-sm mt-1">Your AI Product Manager Assistant</p>
        </div>
      </div>

      <Card className="flex-1 min-h-0 overflow-hidden flex flex-col border-slate-200 bg-white shadow-sm relative rounded-3xl">
        <ScrollArea className="flex-1 min-h-0">
          <div className="space-y-6 flex flex-col p-6 w-full">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-[85%] ${msg.role === "user" ? "self-end flex-row-reverse" : "self-start"}`}
              >
                <Avatar className={`w-8 h-8 border flex items-center justify-center ${msg.role === "user" ? "border-blue-200 bg-blue-50 text-blue-600" : "border-slate-200 bg-white text-blue-600 shadow-sm"}`}>
                  {msg.role === "user" ? <User size={16} /> : <Sparkles size={16} />}
                </Avatar>

                <div className={`space-y-2 ${msg.role === "user" ? "items-end" : "items-start"}`}>
                  <div
                    className={`p-3.5 rounded-3xl text-[15px] leading-relaxed shadow-sm ${msg.role === "user"
                      ? "bg-blue-600 text-white rounded-tr-md whitespace-pre-wrap"
                      : "bg-white text-slate-800 rounded-tl-md border border-slate-100"
                      }`}
                  >
                    {msg.role === "user" ? (
                      msg.content
                    ) : (
                      <ReactMarkdown
                        components={{
                          p: ({ ...props }) => <p className="mb-3 last:mb-0" {...props} />,
                          h1: ({ ...props }) => <h1 className="text-xl font-bold mt-5 mb-3 text-slate-900" {...props} />,
                          h2: ({ ...props }) => <h2 className="text-lg font-bold mt-4 mb-2 text-slate-900" {...props} />,
                          h3: ({ ...props }) => <h3 className="text-base font-semibold mt-3 mb-2 text-slate-900" {...props} />,
                          ul: ({ ...props }) => <ul className="list-disc pl-5 mb-3 space-y-1" {...props} />,
                          ol: ({ ...props }) => <ol className="list-decimal pl-5 mb-3 space-y-1" {...props} />,
                          li: ({ ...props }) => <li className="pl-1" {...props} />,
                          strong: ({ ...props }) => <strong className="font-semibold text-slate-900" {...props} />,
                          a: ({ ...props }) => <a className="text-blue-600 hover:underline" {...props} />,
                          blockquote: ({ ...props }) => <blockquote className="border-l-4 border-slate-200 pl-4 py-1 italic text-slate-600 my-3" {...props} />,
                          code: ({ inline, ...props }: any) =>
                            inline ? <code className="bg-slate-100 px-1.5 py-0.5 rounded text-sm font-mono text-pink-600" {...props} />
                              : <code className="block bg-slate-100 p-3 rounded-md text-sm font-mono my-3 overflow-x-auto text-slate-800" {...props} />
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    )}
                  </div>

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-2 text-sm text-slate-500">
                      <p className="mb-2 text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                        Sources
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {msg.sources.map((src, i) => (
                          <Badge key={i} variant="outline" className="bg-slate-50/50 border-slate-200 text-slate-600 font-medium hover:bg-slate-100 transition-colors">
                            {src.guest}: {src.title}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-3 self-start items-center text-slate-500">
                <Avatar className="w-8 h-8 border border-slate-200 bg-white text-blue-600 shadow-sm flex items-center justify-center">
                  <Sparkles size={16} />
                </Avatar>
                <div className="p-3.5 bg-white shadow-sm rounded-3xl rounded-tl-md border border-slate-100 flex items-center gap-2 text-[15px]">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-600" /> Thinking...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} className="h-px w-full" />
          </div>
        </ScrollArea>

        <CardContent className="p-4 bg-white border-t border-slate-100">
          <form onSubmit={handleSubmit} className="flex gap-3 items-center bg-slate-50 p-2 rounded-full border border-slate-200 focus-within:ring-2 focus-within:ring-blue-100 focus-within:border-blue-400 transition-all shadow-sm">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about product strategy, growth, team building..."
              className="flex-1 bg-transparent border-none shadow-none focus-visible:ring-0 px-4 text-[15px] placeholder:text-slate-400 text-slate-800"
              disabled={isLoading}
            />
            <Button type="submit" disabled={!input.trim() || isLoading} className="bg-blue-600 hover:bg-blue-700 text-white rounded-full w-10 h-10 p-0 shrink-0 shadow-md transition-transform active:scale-95">
              <Send className="w-4 h-4 ml-0.5" />
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
