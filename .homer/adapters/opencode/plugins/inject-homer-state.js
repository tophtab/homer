/* global Bun, process */

import { existsSync } from "fs"

function findRoot(directory) {
  let current = directory
  while (current && current !== "/") {
    if (existsSync(`${current}/.homer`)) return current
    const next = current.replace(/\/[^/]*$/, "") || "/"
    if (next === current) break
    current = next
  }
  return null
}

async function getHomerState(root) {
  const script = `${root}/.homer/scripts/homer.py`
  if (!existsSync(script)) return ""
  const proc = Bun.spawn(["python3", script, "hook-state"], {
    cwd: root,
    stdout: "pipe",
    stderr: "ignore",
  })
  const timeout = new Promise(resolve => setTimeout(() => resolve(null), 2000))
  const done = proc.exited.then(() => proc).catch(() => null)
  const result = await Promise.race([done, timeout])
  if (!result) return ""
  return (await new Response(proc.stdout).text()).trim()
}

export default async ({ directory }) => {
  return {
    "chat.message": async (_input, output) => {
      try {
        if (process.env.HOMER_HOOKS === "0" || process.env.HOMER_DISABLE_HOOKS === "1") {
          return
        }
        const root = findRoot(directory)
        if (!root) return
        const state = await getHomerState(root)
        if (!state) return
        const parts = output?.parts || []
        const index = parts.findIndex(part => part.type === "text" && part.text !== undefined)
        if (index >= 0) {
          parts[index].text = `${state}\n\n${parts[index].text || ""}`
        } else {
          parts.unshift({ type: "text", text: state })
        }
      } catch {
        // Hooks are optional; failures must not interrupt the user turn.
      }
    },
  }
}
