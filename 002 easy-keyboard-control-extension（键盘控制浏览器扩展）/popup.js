/**
 * Popup script for Keyboard Control Extension.
 * Author: ashajia (centos@126.com)
 * GitHub: https://github.com/ashajia
 */
document.getElementById("search-input").focus();

document.getElementById("search-input").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    const searchTerm = event.target.value;
    if (searchTerm) {
      chrome.tabs.create({ url: `https://cn.bing.com/search?q=${encodeURIComponent(searchTerm)}` });
    }
  }
});