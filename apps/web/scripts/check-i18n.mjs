// Çeviri dosyalarında eksik anahtar kontrolü (i18n.md §1):
// tr'de olan her anahtar en'de de olmalı ve tersi. CI'da hata.
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = fileURLToPath(new URL('../src/i18n/', import.meta.url))
const langs = ['tr', 'en']

const flatten = (obj, prefix = '') =>
  Object.entries(obj).flatMap(([k, v]) =>
    typeof v === 'object' && v !== null ? flatten(v, `${prefix}${k}.`) : [`${prefix}${k}`],
  )

let failed = false
const namespaces = new Set(
  langs.flatMap((l) => readdirSync(join(root, l)).filter((f) => f.endsWith('.json'))),
)
for (const ns of namespaces) {
  const keys = {}
  for (const l of langs) {
    try {
      keys[l] = new Set(flatten(JSON.parse(readFileSync(join(root, l, ns), 'utf8'))))
    } catch {
      console.error(`[i18n] ${l}/${ns} eksik`)
      failed = true
      keys[l] = new Set()
    }
  }
  for (const a of langs) {
    for (const b of langs) {
      if (a === b) continue
      for (const k of keys[a]) {
        if (!keys[b].has(k)) {
          console.error(`[i18n] ${ns}: "${k}" ${a} içinde var, ${b} içinde yok`)
          failed = true
        }
      }
    }
  }
}
if (failed) process.exit(1)
console.log(`[i18n] ${namespaces.size} namespace, ${langs.join('/')} tutarlı`)
