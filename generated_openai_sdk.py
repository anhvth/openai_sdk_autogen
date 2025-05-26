from typing import Any, List, Union, Optional, Dict, Tuple, Set, Sequence, Callable, TypeVar, Type
from typing import Optional
from typing import Union
import datetime
import importlib
import inspect
from client_output.client import Client as _GeneratedClient
from client_output.models import *
from client_output.types import UNSET, Unset, File, Response
from pydantic import BaseModel, ConfigDict
from uuid import UUID


import client_output.api.default.create_greeting as _ep_default_create_greeting
import client_output.api.default.health_check as _ep_default_health_check
import client_output.api.default.root_get as _ep_default_root_get






class HelloWorldClient(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    base_url: str

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._raw = _GeneratedClient(base_url=self.base_url)

    def create_greeting(self, *, user_name: str, body: GreetingRequest) -> Union[GreetingResponse, HTTPValidationError, None]:
        return _ep_default_create_greeting.sync(client=self._raw, user_name=user_name, body=body)

    async def create_greeting_async(self, *, user_name: str, body: GreetingRequest) -> Union[GreetingResponse, HTTPValidationError, None]:
        return await _ep_default_create_greeting.asyncio(client=self._raw, user_name=user_name, body=body)

    def health_check(self) -> Optional[HealthResponse]:
        return _ep_default_health_check.sync(client=self._raw)

    async def health_check_async(self) -> Optional[HealthResponse]:
        return await _ep_default_health_check.asyncio(client=self._raw)

    def root_get(self) -> Optional[RootGetResponseRootGet]:
        return _ep_default_root_get.sync(client=self._raw)

    async def root_get_async(self) -> Optional[RootGetResponseRootGet]:
        return await _ep_default_root_get.asyncio(client=self._raw)



if __name__ == '__main__':
    import asyncio
    import inspect # For inspecting namespace methods
    from uuid import uuid4 # Commonly used for IDs

    _pkg_name = "client_output"
    # Models are now expected to be available due to 'from client_output.models import *'
    # We still try to get them by name for the test logic.
    _all_models = {}
    _all_types = {}
    _TestUnset = None
    _TestUNSET_VAL = None

    try:
        _models_module = importlib.import_module(f"{_pkg_name}.models")
        for name, obj in inspect.getmembers(_models_module, inspect.isclass):
            # Check if the model is defined in this models module (not imported from elsewhere)
            if obj.__module__ == _models_module.__name__:
                _all_models[name] = obj
                globals()[name] = obj # Make models available globally for test code
    except ImportError:
        print(f"Warning: Could not import models from {_pkg_name}.models.")

    try:
        _types_module = importlib.import_module(f"{_pkg_name}.types")
        for name, obj in inspect.getmembers(_types_module):
            if not name.startswith('_'): 
                _all_types[name] = obj
                if name in ("Unset", "UNSET", "File", "Response"): # Make common types global for tests
                    globals()[name] = obj
        _TestUnset = _all_types.get('Unset')
        _TestUNSET_VAL = _all_types.get('UNSET')
    except ImportError:
        print(f"Warning: Could not import types from {_pkg_name}.types.")
    
    if _TestUnset is None:
        class _DummyUnset: pass
        _TestUnset = _DummyUnset
        if 'Unset' not in globals(): globals()['Unset'] = _TestUnset
    if _TestUNSET_VAL is None:
        _TestUNSET_VAL = _TestUnset()
        if 'UNSET' not in globals(): globals()['UNSET'] = _TestUNSET_VAL


    # Specific models for the example test part, these will use the globally available ones if imported
    _TestCpRequest = _all_models.get('CreateProjectRequest')
    _TestProject = _all_models.get('Project')
    _TestHttpValidationError = _all_models.get('HTTPValidationError')
    _TestPfResponse = _all_models.get('ProjectFileResponse')
    
    if not all([_TestCpRequest, _TestProject, _TestHttpValidationError, _TestPfResponse]):
        print("Warning: Some specific models for testing (e.g., CreateProjectRequest, Project) were not found via dynamic import. "
              "Parts of the example test code might be skipped or fail if these models are essential for your API.")


    client = HelloWorldClient(base_url='http://localhost:8080') 

    print(f"--- SDK Test for {client.__class__.__name__} (package: {_pkg_name}) ---")

    async def test_method(target_obj: Any, method_name: str, method_callable: Callable[..., Any], prefix: str = ""):
        print(f"{prefix}  Attempting: {method_name}")
        sig = inspect.signature(method_callable)
        is_async = inspect.iscoroutinefunction(method_callable)
        
        try:
            required_params = [
                p for p in sig.parameters.values() 
                if p.default == inspect.Parameter.empty and p.name != 'self'
            ]
            
            can_call_directly = True
            kwargs_to_pass = {}

            for p in required_params:
                param_annotation_name = getattr(p.annotation, '__name__', str(p.annotation))

                is_model_param = hasattr(p.annotation, '__module__') and \
                                 (p.annotation.__module__.startswith(f"{_pkg_name}.models") or \
                                  (param_annotation_name == 'File' and p.annotation.__module__.startswith(f"{_pkg_name}.types")))
                
                is_union_with_model = False
                if hasattr(p.annotation, '__origin__') and p.annotation.__origin__ in (Union, Optional):
                    for arg_type in getattr(p.annotation, '__args__', []):
                        arg_annotation_name = getattr(arg_type, '__name__', str(arg_type))
                        if hasattr(arg_type, '__module__') and \
                           (arg_type.__module__.startswith(f"{_pkg_name}.models") or \
                           (arg_annotation_name == 'File' and arg_type.__module__.startswith(f"{_pkg_name}.types"))):
                            is_union_with_model = True
                            param_annotation_name = arg_annotation_name # Use the model name from Union
                            break
                
                if is_model_param or is_union_with_model:
                    ModelToTry = _all_models.get(param_annotation_name)

                    if ModelToTry and (p.name.lower() == 'body' or 'request' in p.name.lower()):
                        try:
                            kwargs_to_pass[p.name] = ModelToTry() 
                            print(f"{prefix}    - Using dummy '{ModelToTry.__name__}' for '{p.name}'.")
                        except Exception as model_e:
                            print(f"{prefix}    - Could not create dummy '{ModelToTry.__name__}' for '{p.name}': {model_e}. Skipping.")
                            can_call_directly = False
                            break
                    elif param_annotation_name == 'File': # Special handling for File type
                         print(f"{prefix}    - Skipping: requires 'File' parameter '{p.name}' which needs actual file data.")
                         can_call_directly = False
                         break
                    else:
                        print(f"{prefix}    - Skipping: requires complex/unknown model parameter '{p.name}' of type {param_annotation_name or p.annotation}.")
                        can_call_directly = False
                        break
                elif p.annotation == str: kwargs_to_pass[p.name] = "test_string"
                elif p.annotation == int: kwargs_to_pass[p.name] = 123
                elif p.annotation == bool: kwargs_to_pass[p.name] = True
                elif p.annotation == UUID: kwargs_to_pass[p.name] = uuid4()
                else: 
                    print(f"{prefix}    - Skipping: unknown required parameter '{p.name}':{p.annotation}.")
                    can_call_directly = False
                    break

            if not can_call_directly:
                return

            if is_async: result = await method_callable(**kwargs_to_pass)
            else: result = method_callable(**kwargs_to_pass)
            print(f"{prefix}    Result: {result}")

        except Exception as e:
            print(f"{prefix}    Error calling {method_name}: {e}")

    async def run_all_tests():
        for item_name in dir(client):
            if item_name.startswith('_') or item_name in ['model_fields', 'model_config', 'base_url', '_raw']:
                continue
            item_obj = getattr(client, item_name)
            if item_obj is None: continue

            if item_obj.__class__.__name__.startswith('_') and hasattr(item_obj, '_raw'):
                print(f"\n--- Testing Namespace: {item_name} ---")
                for method_name in dir(item_obj):
                    if method_name.startswith('_'): continue
                    method_callable = getattr(item_obj, method_name)
                    if callable(method_callable):
                        await test_method(item_obj, method_name, method_callable, prefix="  ")
        
        print(f"\n--- Testing Top-Level Client Methods ---")
        for method_name in dir(client):
            if method_name.startswith('_') or method_name in ['model_fields', 'model_config', 'base_url', '_raw']:
                continue
            method_callable = getattr(client, method_name)
            if not callable(method_callable) or (hasattr(method_callable, "__self__") and method_callable.__self__.__class__.__name__.startswith('_')):
                 if not callable(method_callable) and hasattr(method_callable, '_raw') and method_callable.__class__.__name__.startswith('_'):
                     continue
            if callable(method_callable):
                 is_namespace_like = hasattr(method_callable, '_raw') and not inspect.isfunction(method_callable) and not inspect.ismethod(method_callable)
                 if is_namespace_like and method_callable.__class__.__name__.endswith("Namespace"):
                     continue
                 await test_method(client, method_name, method_callable, prefix="")
        print("\n--- End of SDK Test ---")

    asyncio.run(run_all_tests())
    print("\nNOTE: Generic test attempts to call parameter-less methods or methods with simple params. "
          "Complex POST/PUT calls with bodies are likely skipped or use dummy empty bodies. "
          "Ensure the API server is running for these tests.")
