import '@testing-library/jest-dom/vitest'

// jsdom has no layout engine; components that measure themselves get a fixed width
class FixedResizeObserver {
  constructor(private callback: ResizeObserverCallback) {}
  observe(target: Element) {
    this.callback([{ target, contentRect: { width: 800, height: 100 } } as ResizeObserverEntry], this as never)
  }
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver = FixedResizeObserver as unknown as typeof ResizeObserver
