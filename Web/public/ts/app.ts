// ========== Interfaces =========
interface UserData {
    user_id: string,
    user_name: string
};

interface UserListData {
    data: Array<UserData>
};

interface UserActiveWindow {
    data: {
        active_window: string,
        update_time: number
    }
};

// DOM Eletments
const users_list: HTMLDivElement = document.getElementsByClassName("usersList")[0] as HTMLDivElement;
const target_user: HTMLParagraphElement = document.getElementById("target-user") as HTMLParagraphElement;
const status_p: HTMLParagraphElement = document.getElementById("status-p") as HTMLParagraphElement;
const activeWindow_p: HTMLParagraphElement = document.getElementById("activeWindow-p") as HTMLParagraphElement;
const update_p: HTMLParagraphElement = document.getElementById("update-time") as HTMLParagraphElement;

// ========== Global Variables =========
let userList: Array<UserData> = [];
let target_user_id: string | undefined = undefined;
let target_user_name: string | undefined = undefined;

// ========== Functions =========
/** 时间戳转日期 */
function timestampToDate(timestamp: number): string {
    if (timestamp == null || timestamp == undefined) return "";
    const date = new Date(timestamp);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

async function render_target(): Promise<void> {
    if (target_user_id === undefined || target_user_name === undefined) {
        return
    }
    const response = await fetch("/users/get", {
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": JSON.stringify({
            "user_id": target_user_id
        })
    })
    if (response.ok) {
        const data: UserActiveWindow = await response.json();
        const unix: number = data.data.update_time;
        const date_format = timestampToDate(unix * 1000);
        const online: boolean = Date.now() / 1000 - unix <= 60;

        target_user.textContent = `Target User: ${target_user_name}`;
        activeWindow_p.textContent = `Active Window: ${data.data.active_window}`;
        update_p.textContent = `Update Time: ${date_format}`;
        if (online) {
            status_p.textContent = "online";
            status_p.className = "online";
        } else {
            status_p.textContent = "disconnect";
            status_p.className = "disconnect";
        }

    } else {
        console.error("Failed to fetch user list");
    }
}

function creatUserCard(text: string, id: string): HTMLDivElement {
    const card: HTMLDivElement = document.createElement("div");
    const card_text: HTMLParagraphElement = document.createElement("p");
    
    card.className = "userCard";
    card_text.textContent = text;

    card.addEventListener("click", async function(): Promise<void> {
        target_user_id = id;
        target_user_name = text;
        render_target();
    })

    card.appendChild(card_text);

    return card;
}

function updateUserListDisplay(): void {
    console.log(userList);

    userList.forEach((user: UserData) => {
        const card: HTMLDivElement = creatUserCard(user.user_name, user.user_id);
        users_list.appendChild(card);
    })
}

async function get_user_list(): Promise<void> {
    const response = await fetch("/users");
    if (response.ok) {
        const data: UserListData = await response.json();
        if (data.data === undefined) {
            console.error("User list data is undefined");
            return;
        }
        userList = data.data.map((user: { user_id: string, user_name: string }) => ({
            user_id: user.user_id,
            user_name: user.user_name
        }));
        updateUserListDisplay();
    } else {
        console.error("Failed to fetch user list");
    }
}


// ========== Initialization =========
get_user_list()
setInterval(render_target, 2000)
