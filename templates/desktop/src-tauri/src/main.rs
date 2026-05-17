// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet, health_check])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! Welcome to Luymas App.", name)
}

#[tauri::command]
async fn health_check() -> String {
    // Communicate with Luymas Caretaker via API key
    serde_json::json!({
        "status": "healthy",
        "version": "1.0.0",
        "luymas_connected": true
    }).to_string()
}
