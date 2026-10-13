// Applies the stored or system colour theme before the first paint (see src/lib/theme.ts)
;(function () {
  var theme = null
  try {
    theme = localStorage.getItem('spur.theme')
  } catch (error) {
    // Storage blocked: follow the system
  }
  if (theme !== 'light' && theme !== 'dark') {
    theme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  document.documentElement.dataset.theme = theme
  var meta = document.querySelector('meta[name="theme-color"]')
  if (meta) meta.setAttribute('content', theme === 'dark' ? '#16181c' : '#ffffff')
})()
