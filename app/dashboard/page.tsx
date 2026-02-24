"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Sidebar from "../components/Sidebar"
import api from "@/lib/api"
import styles from "./dashboard.module.scss"

export default function DashboardPage() {
  const router = useRouter()
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      router.push("/login")
      return
    }
    fetchAgents()
  }, [])

  async function fetchAgents() {
    try {
      const res = await api.get("/agent/list")
      setAgents(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.layout}>
      <Sidebar />

      <main className={styles.main}>
        <div className={styles.header}>
          <div>
            <h1 className={styles.title}>Dashboard</h1>
            <p className={styles.subtitle}>Welcome back to VoiceAI</p>
          </div>
        </div>

        {/* Stats */}
        <div className={styles.stats}>
          <div className={styles.statCard}>
            <p className={styles.statLabel}>Total Agents</p>
            <p className={styles.statValue}>{agents.length}</p>
          </div>
          <div className={styles.statCard}>
            <p className={styles.statLabel}>Total Calls</p>
            <p className={styles.statValue}>0</p>
          </div>
          <div className={styles.statCard}>
            <p className={styles.statLabel}>Minutes Used</p>
            <p className={styles.statValue}>0</p>
          </div>
          <div className={styles.statCard}>
            <p className={styles.statLabel}>Wallet Balance</p>
            <p className={styles.statValue}>₹0</p>
          </div>
        </div>

        {/* Agents List */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <h2>Your Agents</h2>
            <button
              className={styles.btnPrimary}
              onClick={() => router.push("/agents/create")}
            >
              + New Agent
            </button>
          </div>

          {loading ? (
            <p className={styles.empty}>Loading...</p>
          ) : agents.length === 0 ? (
            <div className={styles.emptyState}>
              <p>◈</p>
              <p>No agents yet</p>
              <button
                className={styles.btnPrimary}
                onClick={() => router.push("/agents/create")}
              >
                Create your first agent
              </button>
            </div>
          ) : (
            <div className={styles.agentList}>
              {agents.map((agent: any) => (
                <div key={agent.id} className={styles.agentCard}>
                  <div className={styles.agentInfo}>
                    <p className={styles.agentName}>{agent.name}</p>
                    <p className={styles.agentId}>ID: {agent.bolna_agent_id}</p>
                  </div>
                  <span className={`${styles.badge} ${agent.status === "active" ? styles.active : styles.draft}`}>
                    {agent.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}