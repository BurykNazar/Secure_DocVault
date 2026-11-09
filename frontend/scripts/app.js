import { createWorkspace } from "./components/workspace.js";
import { createGate } from "./components/gate.js";
import { toast } from "./ui/toast.js";

const stage = document.getElementById("gate");

function showGate() {
  stage.replaceChildren(
    createGate({
      onSignedIn(account) {
        document.body.classList.add("app-mode");
        stage.replaceChildren(
          createWorkspace({
            account,
            onLeave() {
              document.body.classList.remove("app-mode");
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
