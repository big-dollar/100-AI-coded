/**
 * Background script for Keyboard Control Extension.
 * Author: ashajia (centos@126.com)
 * GitHub: https://github.com/ashajia
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "close_tab") {
    chrome.tabs.remove(sender.tab.id);
  } else if (message.action === "open_popup") {
    // 打开弹出窗口
    chrome.action.openPopup();
  }
});