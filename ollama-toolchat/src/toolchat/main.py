from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .config import settings
from .infra.logging import setup_logging, get_logger
from .api import routes_chat, routes_health, routes_settings
from .tools.registry import registry
from .tools.disk import DiskFreeTool
from .tools.health import SystemHealthTool
from .tools.photos import OrganizePhotosTool
from .tools.gpu import GPUTemperatureTool
from .tools.directory_size import DirectorySizeTool
from .tools.duplicates import DuplicateFinderTool
from .tools.cmd.specs_storage import (
    create_df_tool, create_du_tool, create_lsblk_tool, create_findmnt_tool
)
from .tools.cmd.specs_perf import (
    create_ps_tool, create_free_tool, create_vmstat_tool, 
    create_iostat_tool, create_uptime_tool
)
from .tools.cmd.specs_logs import create_journalctl_tool, create_dmesg_tool
from .tools.cmd.specs_hw import (
    create_lspci_tool, create_lsusb_tool, create_lscpu_tool, create_sensors_tool
)
from .tools.cmd.specs_system_info import (
    create_uname_tool, create_hostname_tool, create_whoami_tool, create_id_tool,
    create_env_tool, create_timedatectl_tool, create_locale_tool
)
from .tools.cmd.specs_process import (
    create_top_tool, create_htop_tool, create_pidstat_tool, create_iotop_tool
)
from .tools.cmd.specs_network import (
    create_ip_addr_tool, create_ip_route_tool, create_ss_tool, create_nmcli_tool,
    create_ping_tool, create_resolvectl_tool
)
from .tools.cmd.specs_security import (
    create_ufw_status_tool, create_aa_status_tool, create_loginctl_tool
)
from .tools.cmd.specs_power_tools import (
    create_lsof_tool, create_fuser_tool, create_file_tool, create_ldd_tool, create_last_tool
)
from .tools.cmd.specs_file_search import (
    create_find_tool, create_fd_tool, create_rg_tool, create_tree_tool
)
from .tools.cmd.specs_system import (
    create_apt_install_tool, create_apt_update_tool,
    create_systemctl_status_tool, create_systemctl_restart_tool,
    create_systemctl_start_tool, create_systemctl_stop_tool
)

setup_logging(settings.log_level)
logger = get_logger(__name__)

app = FastAPI(
    title="Ollama ToolChat",
    description="Local-first LLM chatbot with safe command execution",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(127\.0\.0\.1|localhost)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router)
app.include_router(routes_chat.router)
app.include_router(routes_settings.router)

web_dir = Path(__file__).parent.parent.parent / "web"
if web_dir.exists():
    app.mount("/", StaticFiles(directory=str(web_dir), html=True), name="static")


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Ollama ToolChat")
    logger.info(f"Ollama URL: {settings.ollama_url}")
    logger.info(f"Model: {settings.ollama_model}")
    logger.info(f"Sandbox mode: {settings.sandbox_mode}")
    
    # Register MVP Python tools
    registry.register(DiskFreeTool())
    registry.register(SystemHealthTool())
    registry.register(OrganizePhotosTool())
    registry.register(GPUTemperatureTool())
    registry.register(DirectorySizeTool())
    registry.register(DuplicateFinderTool())
    
    # Register storage command tools
    try:
        registry.register(create_df_tool())
        registry.register(create_du_tool())
        registry.register(create_lsblk_tool())
        registry.register(create_findmnt_tool())
        logger.info("Registered storage command tools")
    except Exception as e:
        logger.warning(f"Some storage tools unavailable: {e}")
    
    # Register performance command tools
    try:
        registry.register(create_ps_tool())
        registry.register(create_free_tool())
        registry.register(create_vmstat_tool())
        registry.register(create_uptime_tool())
        logger.info("Registered performance command tools")
    except Exception as e:
        logger.warning(f"Some performance tools unavailable: {e}")
    
    # Register iostat if available (requires sysstat package)
    try:
        registry.register(create_iostat_tool())
    except Exception:
        logger.info("iostat not available (install sysstat package)")
    
    # Register log command tools
    try:
        registry.register(create_journalctl_tool())
        registry.register(create_dmesg_tool())
        logger.info("Registered log command tools")
    except Exception as e:
        logger.warning(f"Some log tools unavailable: {e}")
    
    # Register hardware command tools
    try:
        registry.register(create_lspci_tool())
        registry.register(create_lsusb_tool())
        registry.register(create_lscpu_tool())
        logger.info("Registered hardware command tools")
    except Exception as e:
        logger.warning(f"Some hardware tools unavailable: {e}")
    
    # Register system information tools
    try:
        registry.register(create_uname_tool())
        registry.register(create_hostname_tool())
        registry.register(create_whoami_tool())
        registry.register(create_id_tool())
        registry.register(create_env_tool())
        registry.register(create_timedatectl_tool())
        registry.register(create_locale_tool())
        logger.info("Registered system information tools")
    except Exception as e:
        logger.warning(f"Some system info tools unavailable: {e}")
    
    # Register process monitoring tools
    try:
        registry.register(create_top_tool())
        registry.register(create_pidstat_tool())
        logger.info("Registered process monitoring tools")
    except Exception as e:
        logger.warning(f"Some process tools unavailable: {e}")
    
    # Register network tools (only if network is allowed)
    if settings.allow_network:
        try:
            registry.register(create_ip_addr_tool())
            registry.register(create_ip_route_tool())
            registry.register(create_ss_tool())
            registry.register(create_nmcli_tool())
            registry.register(create_ping_tool())
            registry.register(create_resolvectl_tool())
            logger.info("Registered network tools")
        except Exception as e:
            logger.warning(f"Some network tools unavailable: {e}")
    else:
        logger.info("Network tools disabled (ALLOW_NETWORK=false)")
    
    # Register security tools
    try:
        registry.register(create_ufw_status_tool())
        registry.register(create_aa_status_tool())
        registry.register(create_loginctl_tool())
        logger.info("Registered security tools")
    except Exception as e:
        logger.warning(f"Some security tools unavailable: {e}")
    
    # Register power user tools
    try:
        registry.register(create_lsof_tool())
        registry.register(create_fuser_tool())
        registry.register(create_file_tool())
        registry.register(create_ldd_tool())
        registry.register(create_last_tool())
        logger.info("Registered power user diagnostic tools")
    except Exception as e:
        logger.warning(f"Some power tools unavailable: {e}")
    
    # Register file search tools
    try:
        registry.register(create_find_tool())
        registry.register(create_fd_tool())
        registry.register(create_rg_tool())
        registry.register(create_tree_tool())
        logger.info("Registered file search tools")
    except Exception as e:
        logger.warning(f"Some file search tools unavailable: {e}")
    
    # Register sensors if available (requires lm-sensors package)
    try:
        registry.register(create_sensors_tool())
    except Exception:
        logger.info("sensors not available (install lm-sensors package)")
    
    # Register Tier 2 system management tools (require sudo)
    try:
        registry.register(create_systemctl_status_tool())
        logger.info("Registered systemctl status tool")
    except Exception as e:
        logger.warning(f"systemctl tools unavailable: {e}")
    
    # Only register Tier 2 write tools if explicitly enabled
    # These require proper sudoers configuration
    tier2_enabled = settings.sandbox_mode != "none"  # Safety: only enable with sandbox
    if tier2_enabled:
        try:
            registry.register(create_apt_install_tool())
            registry.register(create_apt_update_tool())
            registry.register(create_systemctl_restart_tool())
            registry.register(create_systemctl_start_tool())
            registry.register(create_systemctl_stop_tool())
            logger.info("Registered Tier 2 system management tools (sudo required)")
        except Exception as e:
            logger.warning(f"Tier 2 system tools unavailable: {e}")
    else:
        logger.info("Tier 2 system tools disabled (enable sandbox_mode to use)")
    
    logger.info(f"Registered {len(registry.list_tools())} tools total")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Ollama ToolChat")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "toolchat.main:app",
        host=settings.toolchat_host,
        port=settings.toolchat_port,
        reload=False,
    )
