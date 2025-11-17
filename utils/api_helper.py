import requests
import json
import time
from typing import Dict, Any, Optional


class KytosAPIHelper:
    """Helper class for Kytos API interactions"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def create_evc(self, evc_data: Dict[str, Any]) -> requests.Response:
        """Create EVC via API"""
        url = f"{self.base_url}/api/kytos/mef_eline/v2/evc/"
        response = self.session.post(url, json=evc_data)
        return response
    
    def get_evc(self, circuit_id: str) -> requests.Response:
        """Get EVC by circuit ID"""
        url = f"{self.base_url}/api/kytos/mef_eline/v2/evc/{circuit_id}"
        response = self.session.get(url)
        return response
    
    def list_evcs(self) -> requests.Response:
        """List all EVCs"""
        url = f"{self.base_url}/api/kytos/mef_eline/v2/evc/"
        response = self.session.get(url)
        return response
    
    def delete_evc(self, circuit_id: str) -> requests.Response:
        """Delete EVC by circuit ID"""
        url = f"{self.base_url}/api/kytos/mef_eline/v2/evc/{circuit_id}"
        response = self.session.delete(url)
        return response
    
    def verify_evc_created(self, circuit_name: str, timeout: int = 30) -> Optional[str]:
        """
        Verify EVC was created by checking the API
        Returns circuit_id if found, None if not found or timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.list_evcs()
                if response.status_code == 200:
                    evcs = response.json()
                    for circuit_id, evc_data in evcs.items():
                        if evc_data.get('name') == circuit_name:
                            return circuit_id
                time.sleep(2)
            except Exception as e:
                print(f"Error checking EVC status: {e}")
                time.sleep(2)
        return None
    
    def cleanup_test_circuits(self, circuit_names: list):
        """Clean up test circuits by name"""
        try:
            response = self.list_evcs()
            if response.status_code == 200:
                evcs = response.json()
                for circuit_id, evc_data in evcs.items():
                    if evc_data.get('name') in circuit_names:
                        print(f"Cleaning up circuit: {evc_data.get('name')}")
                        delete_response = self.delete_evc(circuit_id)
                        if delete_response.status_code in [200, 204]:
                            print(f"Successfully deleted circuit: {circuit_id}")
                        else:
                            print(f"Failed to delete circuit {circuit_id}: {delete_response.status_code}")
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def build_evc_payload(self, name: str, endpoint_a: str, vlan_a: str, 
                         endpoint_z: str, vlan_z: str, **kwargs) -> Dict[str, Any]:
        """Build EVC API payload from test parameters"""
        
        # Parse VLAN values (handle both single values and ranges)
        def parse_vlan(vlan_str):
            if vlan_str.startswith("[[") and vlan_str.endswith("]]"):
                # Range format: [[100, 200]]
                range_str = vlan_str[2:-2]
                start, end = map(int, range_str.split(", "))
                return {"tag_type": "vlan", "value": [[start, end]]}
            else:
                # Single value
                return {"tag_type": "vlan", "value": int(vlan_str)}
        
        payload = {
            "name": name,
            "uni_a": {
                "interface_id": endpoint_a,
                "tag": parse_vlan(vlan_a)
            },
            "uni_z": {
                "interface_id": endpoint_z,
                "tag": parse_vlan(vlan_z)
            }
        }
        
        # Add optional fields if provided
        if kwargs.get("service_level"):
            payload["service_level"] = int(kwargs["service_level"])
        
        if kwargs.get("priority"):
            payload["priority"] = kwargs["priority"]
        
        if kwargs.get("max_paths"):
            payload["max_paths"] = int(kwargs["max_paths"])
        
        if kwargs.get("qos_queue"):
            payload["queue_id"] = kwargs["qos_queue"]
        
        if kwargs.get("enable_int"):
            payload["enable_int"] = kwargs["enable_int"]
        
        return payload
    
    def wait_for_circuit_active(self, circuit_id: str, timeout: int = 60) -> bool:
        """Wait for circuit to become active"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.get_evc(circuit_id)
                if response.status_code == 200:
                    evc_data = response.json()
                    status = evc_data.get('active', False)
                    if status:
                        return True
                time.sleep(3)
            except Exception as e:
                print(f"Error checking circuit status: {e}")
                time.sleep(3)
        return False