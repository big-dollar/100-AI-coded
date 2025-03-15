/**
 * Background script for Keyboard Control Extension.
 * Author: ashajia (centos@126.com)
 * GitHub: https://github.com/ashajia
 */
document.addEventListener("keydown", (event) => {
  switch (event.key) {
    case "w":
      window.scrollBy(0, -100); // 向上滚动
      break;
    case "s":
      window.scrollBy(0, 100); // 向下滚动
      break;
    case "a":
      history.back(); // 上一个网页
      break;
    case "d":
      history.forward(); // 下一个网页
      break;
    case "x":
      chrome.runtime.sendMessage({ action: "close_tab" }); // 关闭当前网页
      break;
    case "r":
      location.reload(); // 刷新当前网页
      break;
    case "q":
      window.scrollTo(0, 0); // 定位到页面顶部
      break;
    case "e":
      window.scrollTo(0, document.body.scrollHeight); // 定位到页面底部
      break;
    case "f":
      // 触发弹出窗口
      chrome.runtime.sendMessage({ action: "open_popup" });
      break;
  }
});