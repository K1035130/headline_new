import { defineStore } from 'pinia';

export const useLanguageStore = defineStore('language', {
  state: () => ({
    currentLanguage: localStorage.getItem('language') || 'en-US', // 默认英文
  }),
  
  getters: {
    getCurrentLanguage: (state) => state.currentLanguage,
  },
  
  actions: {
    setLanguage(language) {
      this.currentLanguage = language;
      localStorage.setItem('language', language);
    },
  }
});