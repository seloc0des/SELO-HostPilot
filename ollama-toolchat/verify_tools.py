#!/usr/bin/env python3
"""Verify all tools can be created without errors."""

import sys
sys.path.insert(0, 'src')

def test_tool_creation():
    """Test that all tool creation functions work."""
    
    print("\n" + "="*60)
    print("TOOL CREATION VERIFICATION")
    print("="*60 + "\n")
    
    errors = []
    success_count = 0
    
    # Test system info tools
    print("Testing System Information Tools...")
    try:
        from toolchat.tools.cmd.specs_system_info import (
            create_uname_tool, create_hostname_tool, create_whoami_tool, 
            create_id_tool, create_env_tool, create_timedatectl_tool, create_locale_tool
        )
        for func in [create_uname_tool, create_hostname_tool, create_whoami_tool, 
                     create_id_tool, create_env_tool, create_timedatectl_tool, create_locale_tool]:
            tool = func()
            print(f"  ✓ {tool.spec.name}")
            success_count += 1
    except Exception as e:
        errors.append(f"System Info: {e}")
        print(f"  ✗ Error: {e}")
    
    # Test process tools
    print("\nTesting Process Monitoring Tools...")
    try:
        from toolchat.tools.cmd.specs_process import (
            create_top_tool, create_htop_tool, create_pidstat_tool, create_iotop_tool
        )
        for func in [create_top_tool, create_htop_tool, create_pidstat_tool, create_iotop_tool]:
            tool = func()
            print(f"  ✓ {tool.spec.name}")
            success_count += 1
    except Exception as e:
        errors.append(f"Process: {e}")
        print(f"  ✗ Error: {e}")
    
    # Test network tools
    print("\nTesting Network Tools...")
    try:
        from toolchat.tools.cmd.specs_network import (
            create_ip_addr_tool, create_ip_route_tool, create_ss_tool, 
            create_nmcli_tool, create_ping_tool, create_resolvectl_tool
        )
        for func in [create_ip_addr_tool, create_ip_route_tool, create_ss_tool, 
                     create_nmcli_tool, create_ping_tool, create_resolvectl_tool]:
            tool = func()
            print(f"  ✓ {tool.spec.name}")
            success_count += 1
    except Exception as e:
        errors.append(f"Network: {e}")
        print(f"  ✗ Error: {e}")
    
    # Test security tools
    print("\nTesting Security Tools...")
    try:
        from toolchat.tools.cmd.specs_security import (
            create_ufw_status_tool, create_aa_status_tool, create_loginctl_tool
        )
        for func in [create_ufw_status_tool, create_aa_status_tool, create_loginctl_tool]:
            tool = func()
            print(f"  ✓ {tool.spec.name}")
            success_count += 1
    except Exception as e:
        errors.append(f"Security: {e}")
        print(f"  ✗ Error: {e}")
    
    # Test power tools
    print("\nTesting Power User Tools...")
    try:
        from toolchat.tools.cmd.specs_power_tools import (
            create_lsof_tool, create_fuser_tool, create_file_tool, 
            create_ldd_tool, create_last_tool
        )
        for func in [create_lsof_tool, create_fuser_tool, create_file_tool, 
                     create_ldd_tool, create_last_tool]:
            tool = func()
            print(f"  ✓ {tool.spec.name}")
            success_count += 1
    except Exception as e:
        errors.append(f"Power Tools: {e}")
        print(f"  ✗ Error: {e}")
    
    # Test file search tools
    print("\nTesting File Search Tools...")
    try:
        from toolchat.tools.cmd.specs_file_search import (
            create_find_tool, create_fd_tool, create_rg_tool, create_tree_tool
        )
        for func in [create_find_tool, create_fd_tool, create_rg_tool, create_tree_tool]:
            tool = func()
            print(f"  ✓ {tool.spec.name}")
            success_count += 1
    except Exception as e:
        errors.append(f"File Search: {e}")
        print(f"  ✗ Error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✓ Successfully created: {success_count} tools")
    if errors:
        print(f"✗ Errors: {len(errors)}")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print("✓ All new tools created successfully!")
        return 0

if __name__ == '__main__':
    sys.exit(test_tool_creation())
