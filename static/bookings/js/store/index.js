export const Store = (initial = {}) => {
  let state = { ...initial };
  const listeners = new Set();

  return {
    get     : () => state,
    set     : (updater) => {
      state = typeof updater === 'function' ? updater(state) : { ...state, ...updater };
      listeners.forEach(l => l(state));
    },
    subscribe : (fn) => { listeners.add(fn); return () => listeners.delete(fn); }
  };
};