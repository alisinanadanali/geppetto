// i18n kurulumu (ADR-0010, i18n.md §1). tr varsayılan; en her sürümde tam.
// Namespace = modül: common, errors, glossary, stock, materials, import, cutplan, orders, machines.
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import enCommon from './en/common.json'
import trCommon from './tr/common.json'

export const defaultNS = 'common'
export const resources = {
  tr: { common: trCommon },
  en: { common: enCommon },
} as const

void i18n.use(initReactI18next).init({
  resources,
  lng: 'tr',
  fallbackLng: 'tr',
  defaultNS,
  interpolation: { escapeValue: false },
})

export default i18n
