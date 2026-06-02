import { getConfig } from "newsroom-core/assets/utils";
import { login } from "./auth0";

const handlePrManagerClick = (event: Event) => {
  event.preventDefault();
  fetch("/cp_session")
    .then((r) => (r.ok ? process.env.AUTH0_FIREBASE_CONNECTION : undefined))
    .then(login)
    .catch(login);
};

const prManagerObserver = new MutationObserver((_, observer) => {
  const element = document.querySelector(
    '[data-test-id="sidenav-link-pr_manager"]',
  );
  if (element) {
    observer.disconnect();
    element.addEventListener("click", handlePrManagerClick);
  }
});

const element = document.querySelector(
  '[data-test-id="sidenav-link-pr_manager"]',
);
if (element) {
  element.addEventListener("click", handlePrManagerClick);
} else if (getConfig("prManagerSidenavEnabled")) {
  prManagerObserver.observe(document.body, {
    childList: true,
    subtree: true,
  });
}
