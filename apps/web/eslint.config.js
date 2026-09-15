// ESLint flat config. Kurallar ADR-0010 ve design-direction.md'den:
//  - JSX'te çıplak metin yasak (i18next/no-literal-string)
//  - Elle yazılmış API tipi yasak: src/api/generated dışında API tipi tanımlanmaz (bölüm 5.9'da sıkılaştırılır)
//  - Elle hex/px yasak: bölüm 7.1'de token lint kuralı eklenir
import js from '@eslint/js'
import i18next from 'eslint-plugin-i18next'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import globals from 'globals'
import tseslint from 'typescript-eslint'

export default tseslint.config(
  { ignores: ['dist', 'node_modules', 'src/api/generated'] },
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      ...tseslint.configs.recommended,
      reactHooks.configs['recommended-latest'],
      reactRefresh.configs.vite,
      i18next.configs['flat/recommended'],
    ],
    languageOptions: { ecmaVersion: 2023, globals: globals.browser },
    rules: {
      'i18next/no-literal-string': [
        'error',
        {
          mode: 'jsx-text-only',
          'jsx-attributes': { include: ['title', 'placeholder', 'aria-label', 'alt'] },
        },
      ],
    },
  },
)
