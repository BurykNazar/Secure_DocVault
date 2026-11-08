import { createAccountView } from "./components/account-view.js";
import { createGate } from "./components/gate.js";
import { toast } from "./ui/toast.js";

const stage = document.getElementById("gate");

function showGate() {
  stage.replaceChildren(
    createGate({
      onSignedIn(account) {
        stage.replaceChildren(
          createAccountView({
            account,
            onLeave() {
              showGate();
              toast("Ви вийшли з облікового запису.");
            },
          })
        );
        toast(`Вітаємо, ${account.username}!`);
      },
    })
  );
}

showGate();
