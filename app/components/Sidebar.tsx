"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import styles from "./Sidebar.module.scss"

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: "⊞" },
  { label: "Agents", href: "/agents", icon: "◈" },
  { label: "Calls", href: "/calls", icon: "◎" },
  { label: "Settings", href: "/settings", icon: "⚙" },
]

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()

  function handleLogout() {
    localStorage.removeItem("token")
    router.push("/login")
  }

  return (
    <aside className={styles.sidebar}>
      {/* Logo */}
      <div className={styles.logo}>
        <div className={styles.logoIcon}>V</div>
        <span>VoiceAI</span>
      </div>

      {/* Nav */}
      <nav className={styles.nav}>
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`${styles.navItem} ${pathname === item.href ? styles.active : ""}`}
          >
            <span className={styles.icon}>{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      {/* Logout */}
      <button onClick={handleLogout} className={styles.logout}>
        ↩ Logout
      </button>
    </aside>
  )
}