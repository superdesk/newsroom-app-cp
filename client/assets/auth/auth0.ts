import { Auth0Client, createAuth0Client } from "@auth0/auth0-spa-js";

let auth0Client: Auth0Client;
let init: Promise<void> | null = null;

function initAuth0() {
  if (init) return init;

  init = (async () => {
    try {
      auth0Client = await createAuth0Client({
        domain: process.env.AUTH0_DOMAIN!,
        clientId: process.env.AUTH0_CLIENT_ID!,
        authorizationParams: {
          redirect_uri: process.env.AUTH0_REDIRECT_URI,
        },
      });

      if (
        window.location.search.includes("code=") &&
        window.location.search.includes("state=")
      ) {
        await auth0Client.handleRedirectCallback();
        window.history.replaceState(
          {},
          document.title,
          window.location.pathname,
        );
      }
    } catch (err) {
      console.error("Initialization error:", err);
      init = null;
    }
  })();
  return init;
}

async function login(connection?: string) {
  await initAuth0();

  try {
    return await auth0Client.loginWithRedirect({
      authorizationParams: { connection },
    });
  } catch (err) {
    console.error(err);
  }
}

initAuth0();

export { login };
