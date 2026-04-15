#[cfg(target_os = "windows")]
extern "C" {
    fn FreeConsole();
}

fn main() {
    // Hide console window on Windows
    #[cfg(target_os = "windows")]
    unsafe {
        FreeConsole();
    }

    sys_monitor_lib::run();
}
