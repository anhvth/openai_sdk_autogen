#!/usr/bin/env python3
"""
generate_wrapper.py

Create an OpenAI–style SDK wrapper for a code-base produced by
`openapi-python-client`.

USAGE
-----
python generate_wrapper.py \
       --package <your_client_package_name> \
       --output  <your_sdk_file_name>.py
"""

import argparse
import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Any, Set, List, Dict, Tuple, Union, Optional, Type


def get_pascal_case(name: str) -> str:
    """Converts snake_case or kebab-case to PascalCase."""
    return "".join(word.capitalize() for word in name.replace("-", "_").split("_"))


def format_type_annotation(type_obj: Any, client_pkg_name: str) -> tuple[str, Set[str]]:
    """
    Formats a type annotation for the SDK and collects necessary imports.
    Now, it will not add individual model imports if a wildcard import is used.
    """
    imports: Set[str] = set()

    if type_obj is inspect.Signature.empty or type_obj is Any:
        imports.add("from typing import Any")
        return "Any", imports
    if type_obj is None or type_obj is type(None):
        return "None", imports

    module_name = getattr(type_obj, "__module__", "")
    type_name = getattr(type_obj, "__qualname__", getattr(type_obj, "__name__", ""))

    if not type_name and str(type_obj).lower() == "nonetype":
        return "None", imports

    if hasattr(type_obj, "__origin__"):
        origin = type_obj.__origin__
        origin_module = getattr(origin, "__module__", "")
        origin_name = getattr(
            origin, "__qualname__", getattr(origin, "__name__", "UnknownOrigin")
        )

        if origin_module == "typing":
            args_str_list = []
            valid_args_exist = False
            for arg in getattr(type_obj, "__args__", []):
                arg_str, arg_imports = format_type_annotation(arg, client_pkg_name)
                args_str_list.append(arg_str)
                imports.update(arg_imports)
                if arg_str != "Any":
                    valid_args_exist = True

            if not valid_args_exist and origin_name == "Union":
                imports.add("from typing import Any")
                return "Any", imports

            if (
                origin_name == "Union"
                and "None" in args_str_list
                and len(args_str_list) == 2
            ):
                non_none_arg = next(s for s in args_str_list if s != "None")
                imports.add("from typing import Optional")
                return f"Optional[{non_none_arg}]", imports

            typing_generics_to_import = {
                "List": "List",
                "Dict": "Dict",
                "Tuple": "Tuple",
                "Set": "Set",
                "Sequence": "Sequence",
                "Callable": "Callable",
                "Union": "Union",
                "TypeVar": "TypeVar",
                "Optional": "Optional",
                "Type": "Type",
            }
            if origin_name in typing_generics_to_import:
                imports.add(
                    f"from typing import {typing_generics_to_import[origin_name]}"
                )
            elif origin_name != "Any":
                imports.add(f"from typing import {origin_name}")

            formatted_args = ", ".join(args_str_list)
            return f"{origin_name}[{formatted_args}]", imports
        else:
            if origin_module and origin_module != "builtins":
                imports.add(f"from {origin_module} import {origin_name}")
            args_str_list = []
            for arg in getattr(type_obj, "__args__", []):
                arg_str, arg_imports = format_type_annotation(arg, client_pkg_name)
                args_str_list.append(arg_str)
                imports.update(arg_imports)
            formatted_args = ", ".join(args_str_list)
            return f"{origin_name}[{formatted_args}]", imports

    if module_name == "builtins":
        return type_name, imports

    # For models, we now just return the type_name, assuming wildcard import handles it.
    if module_name.startswith(f"{client_pkg_name}.models"):
        # No individual import added here due to wildcard import strategy
        return type_name, imports

    if module_name == f"{client_pkg_name}.types" and type_name:
        imports.add(f"from {client_pkg_name}.types import {type_name}")
        return type_name, imports

    if module_name == "uuid" and type_name == "UUID":
        imports.add("from uuid import UUID")
        return "UUID", imports

    if module_name == "datetime" and type_name in ("datetime", "date", "time"):
        imports.add(f"from datetime import {type_name}")
        return type_name, imports

    if module_name and module_name not in ("typing",):
        try:
            top_module = module_name.split(".")[0]
            imports.add(f"import {top_module}")
            return f"{module_name}.{type_name}", imports
        except Exception:
            pass

    final_type_str = str(type_obj)  # Keep full path if not a model
    if not type_name and not final_type_str:
        imports.add("from typing import Any")
        return "Any", imports
    return final_type_str or "Any", imports


SDK_TEST_CODE_TEMPLATE = """
if __name__ == '__main__':
    import asyncio
    import inspect # For inspecting namespace methods
    from uuid import uuid4 # Commonly used for IDs

    _pkg_name = "{pkg_name}"
    # Models are now expected to be available due to 'from {pkg_name}.models import *'
    # We still try to get them by name for the test logic.
    _all_models = {{}}
    _all_types = {{}}
    _TestUnset = None
    _TestUNSET_VAL = None

    try:
        _models_module = importlib.import_module(f"{{_pkg_name}}.models")
        for name, obj in inspect.getmembers(_models_module, inspect.isclass):
            # Check if the model is defined in this models module (not imported from elsewhere)
            if obj.__module__ == _models_module.__name__:
                _all_models[name] = obj
                globals()[name] = obj # Make models available globally for test code
    except ImportError:
        print(f"Warning: Could not import models from {{_pkg_name}}.models.")

    try:
        _types_module = importlib.import_module(f"{{_pkg_name}}.types")
        for name, obj in inspect.getmembers(_types_module):
            if not name.startswith('_'): 
                _all_types[name] = obj
                if name in ("Unset", "UNSET", "File", "Response"): # Make common types global for tests
                    globals()[name] = obj
        _TestUnset = _all_types.get('Unset')
        _TestUNSET_VAL = _all_types.get('UNSET')
    except ImportError:
        print(f"Warning: Could not import types from {{_pkg_name}}.types.")
    
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


    client = {sdk_class}(base_url='http://localhost:8080') 

    print(f"--- SDK Test for {{client.__class__.__name__}} (package: {{_pkg_name}}) ---")

    async def test_method(target_obj: Any, method_name: str, method_callable: Callable[..., Any], prefix: str = ""):
        print(f"{{prefix}}  Attempting: {{method_name}}")
        sig = inspect.signature(method_callable)
        is_async = inspect.iscoroutinefunction(method_callable)
        
        try:
            required_params = [
                p for p in sig.parameters.values() 
                if p.default == inspect.Parameter.empty and p.name != 'self'
            ]
            
            can_call_directly = True
            kwargs_to_pass = {{}}

            for p in required_params:
                param_annotation_name = getattr(p.annotation, '__name__', str(p.annotation))

                is_model_param = hasattr(p.annotation, '__module__') and \\
                                 (p.annotation.__module__.startswith(f"{{_pkg_name}}.models") or \\
                                  (param_annotation_name == 'File' and p.annotation.__module__.startswith(f"{{_pkg_name}}.types")))
                
                is_union_with_model = False
                if hasattr(p.annotation, '__origin__') and p.annotation.__origin__ in (Union, Optional):
                    for arg_type in getattr(p.annotation, '__args__', []):
                        arg_annotation_name = getattr(arg_type, '__name__', str(arg_type))
                        if hasattr(arg_type, '__module__') and \\
                           (arg_type.__module__.startswith(f"{{_pkg_name}}.models") or \\
                           (arg_annotation_name == 'File' and arg_type.__module__.startswith(f"{{_pkg_name}}.types"))):
                            is_union_with_model = True
                            param_annotation_name = arg_annotation_name # Use the model name from Union
                            break
                
                if is_model_param or is_union_with_model:
                    ModelToTry = _all_models.get(param_annotation_name)

                    if ModelToTry and (p.name.lower() == 'body' or 'request' in p.name.lower()):
                        try:
                            kwargs_to_pass[p.name] = ModelToTry() 
                            print(f"{{prefix}}    - Using dummy '{{ModelToTry.__name__}}' for '{{p.name}}'.")
                        except Exception as model_e:
                            print(f"{{prefix}}    - Could not create dummy '{{ModelToTry.__name__}}' for '{{p.name}}': {{model_e}}. Skipping.")
                            can_call_directly = False
                            break
                    elif param_annotation_name == 'File': # Special handling for File type
                         print(f"{{prefix}}    - Skipping: requires 'File' parameter '{{p.name}}' which needs actual file data.")
                         can_call_directly = False
                         break
                    else:
                        print(f"{{prefix}}    - Skipping: requires complex/unknown model parameter '{{p.name}}' of type {{param_annotation_name or p.annotation}}.")
                        can_call_directly = False
                        break
                elif p.annotation == str: kwargs_to_pass[p.name] = "test_string"
                elif p.annotation == int: kwargs_to_pass[p.name] = 123
                elif p.annotation == bool: kwargs_to_pass[p.name] = True
                elif p.annotation == UUID: kwargs_to_pass[p.name] = uuid4()
                else: 
                    print(f"{{prefix}}    - Skipping: unknown required parameter '{{p.name}}':{{p.annotation}}.")
                    can_call_directly = False
                    break

            if not can_call_directly:
                return

            if is_async: result = await method_callable(**kwargs_to_pass)
            else: result = method_callable(**kwargs_to_pass)
            print(f"{{prefix}}    Result: {{result}}")

        except Exception as e:
            print(f"{{prefix}}    Error calling {{method_name}}: {{e}}")

    async def run_all_tests():
        for item_name in dir(client):
            if item_name.startswith('_') or item_name in ['model_fields', 'model_config', 'base_url', '_raw']:
                continue
            item_obj = getattr(client, item_name)
            if item_obj is None: continue

            if item_obj.__class__.__name__.startswith('_') and hasattr(item_obj, '_raw'):
                print(f"\\n--- Testing Namespace: {{item_name}} ---")
                for method_name in dir(item_obj):
                    if method_name.startswith('_'): continue
                    method_callable = getattr(item_obj, method_name)
                    if callable(method_callable):
                        await test_method(item_obj, method_name, method_callable, prefix="  ")
        

    asyncio.run(run_all_tests())
    print("\\nNOTE: Generic test attempts to call parameter-less methods or methods with simple params. "
          "Complex POST/PUT calls with bodies are likely skipped or use dummy empty bodies. "
          "Ensure the API server is running for these tests.")
"""


def collect_namespaces(pkg_name: str) -> Dict[str, List[str]]:
    api_pkg = f"{pkg_name}.api"
    try:
        api_module = importlib.import_module(api_pkg)
    except ImportError:
        print(
            f"Error: Could not import API package '{api_pkg}'. Ensure package is installed and accessible."
        )
        return {}

    api_path = Path(api_module.__file__).parent
    mapping: Dict[str, List[str]] = {}
    for mod_info in pkgutil.walk_packages([str(api_path)], prefix=f"{api_pkg}."):
        if mod_info.ispkg:
            continue
        module_name = mod_info.name
        namespace = module_name.split(".")[-2]
        mapping.setdefault(namespace, []).append(module_name)
    return mapping


def render_wrapper(pkg_name: str, sdk_class_name: str) -> str:
    ns_map = collect_namespaces(pkg_name)
    if not ns_map:
        print(
            f"Warning: No API namespaces found for package '{pkg_name}'. Generated SDK will be minimal."
        )

    UNSET_type_actual: Type[Any]
    try:
        _client_types_module = importlib.import_module(f"{pkg_name}.types")
        UNSET_object = getattr(_client_types_module, "UNSET")
        UNSET_type_actual = type(UNSET_object)
    except (ImportError, AttributeError):

        class _PlaceholderUnsetType:
            pass

        UNSET_type_actual = _PlaceholderUnsetType

    sdk_imports: Set[str] = {
        "from typing import Any, List, Union, Optional, Dict, Tuple, Set, Sequence, Callable, TypeVar, Type",
        "from pydantic import BaseModel, ConfigDict",
        f"from {pkg_name}.client import Client as _GeneratedClient",
        "from uuid import UUID",
        "import datetime",
        "import importlib",
        "import inspect",
        f"from {pkg_name}.models import *",  # Wildcard import for models
    }
    try:
        importlib.import_module(f"{pkg_name}.types")
        sdk_imports.add(f"from {pkg_name}.types import UNSET, Unset, File, Response")
    except ImportError:
        print(
            f"Warning: Could not import from {pkg_name}.types. Built-in File, Unset, UNSET, Response might be missing."
        )

    endpoint_module_imports: Set[str] = set()
    namespace_class_definitions: List[str] = []
    client_fields: List[str] = []
    client_inits: List[str] = []
    top_level_method_definitions: List[str] = []

    for ns_name, endpoint_module_paths in sorted(ns_map.items()):
        is_default_namespace = ns_name == "default"

        pascal_ns_name = get_pascal_case(ns_name)
        ns_class_name = f"_{pascal_ns_name}Namespace"

        if not is_default_namespace:
            client_fields.append(
                f"    {ns_name}: Optional[{ns_class_name}] = None"
            )
            client_inits.append(
                f"    self.{ns_name} = {ns_class_name}(self._raw)"
            )

            current_ns_class_code: List[str] = [
                f"class {ns_class_name}:",
                "    _raw: _GeneratedClient",
                "",
                "    def __init__(self, raw_client: _GeneratedClient):",
                "        self._raw = raw_client",
                "",
            ]
        else:
            current_ns_class_code = top_level_method_definitions

        for endpoint_module_path in sorted(endpoint_module_paths):
            endpoint_name = endpoint_module_path.split(".")[-1]
            endpoint_module_alias = f"_ep_{ns_name}_{endpoint_name}"
            endpoint_module_imports.add(
                f"import {endpoint_module_path} as {endpoint_module_alias}"
            )

            try:
                _mod = importlib.import_module(endpoint_module_path)
            except ImportError as e:
                print(
                    f"Warning: Could not import endpoint module {endpoint_module_path}: {e}"
                )
                continue

            for func_type in ["sync", "asyncio"]:
                if not hasattr(_mod, func_type):
                    continue

                original_fn = getattr(_mod, func_type)
                sig = inspect.signature(original_fn)
                params_list_for_sig: List[str] = []
                call_args_list: List[str] = ["client=self._raw"]

                for p_name, p_obj in sig.parameters.items():
                    if p_name == "client":
                        continue
                    param_type_str, param_imports_collected = format_type_annotation(
                        p_obj.annotation, pkg_name
                    )
                    sdk_imports.update(param_imports_collected)
                    param_sig_part = f"{p_name}: {param_type_str}"
                    if p_obj.default is not inspect.Parameter.empty:
                        if isinstance(p_obj.default, UNSET_type_actual):
                            param_sig_part += " = UNSET"
                        else:
                            param_sig_part += f" = {p_obj.default!r}"
                    params_list_for_sig.append(param_sig_part)
                    call_args_list.append(f"{p_name}={p_name}")

                params_str_for_sig = ", ".join(params_list_for_sig)
                call_args_str = ", ".join(call_args_list)
                return_type_str, return_imports_collected = format_type_annotation(
                    sig.return_annotation, pkg_name
                )
                sdk_imports.update(return_imports_collected)

                method_signature_parts = ["self"]
                if params_str_for_sig:
                    method_signature_parts.append("*")
                    method_signature_parts.append(params_str_for_sig)
                method_signature = ", ".join(method_signature_parts)

                method_name = endpoint_name
                if func_type == "asyncio":
                    method_name += "_async"
                    current_ns_class_code.append(
                        f"async def {method_name}({method_signature}) -> {return_type_str}:"
                    )
                    current_ns_class_code.append(
                        f"    return await {endpoint_module_alias}.{func_type}({call_args_str})"
                    )
                else:
                    current_ns_class_code.append(
                        f"def {method_name}({method_signature}) -> {return_type_str}:"
                    )
                    current_ns_class_code.append(
                        f"    return {endpoint_module_alias}.{func_type}({call_args_str})"
                    )
                current_ns_class_code.append("")

        if not is_default_namespace:
            if current_ns_class_code and not current_ns_class_code[-1] == "":
                current_ns_class_code.append("")
            namespace_class_definitions.append("\n".join(current_ns_class_code))

    if top_level_method_definitions and top_level_method_definitions[-1] != "":
        top_level_method_definitions.append("")

    has_specific_typing_import = any(
        imp.startswith("from typing import ") and "Any" not in imp
        for imp in sdk_imports
    )
    is_any_explicitly_used_in_ns = any(
        "-> Any" in line or ": Any" in line
        for ns_class_def in namespace_class_definitions
        for line in ns_class_def.splitlines()
    )
    is_any_explicitly_used_in_top = any(
        "-> Any" in line or ": Any" in line for line in top_level_method_definitions
    )
    is_any_explicitly_used = (
        is_any_explicitly_used_in_ns or is_any_explicitly_used_in_top
    )

    if (
        has_specific_typing_import
        and "from typing import Any" in sdk_imports
        and not is_any_explicitly_used
    ):
        sdk_imports.discard("from typing import Any")

    sorted_sdk_imports = sorted(
        list(sdk_imports),
        key=lambda x: (not x.startswith("from typing"), x.startswith("from "), x),
    )

    code_parts = [
        "\n".join(sorted_sdk_imports),
        "\n",
        "\n".join(sorted(list(endpoint_module_imports))),
        "\n\n",
        "\n\n".join(namespace_class_definitions),
        "\n",
        f"class {sdk_class_name}(BaseModel):",
        "    model_config = ConfigDict(arbitrary_types_allowed=True)",
        "",
        "    base_url: str",
    ]
    code_parts.extend(client_fields)
    code_parts.extend(
        ["", "    def __init__(self, **data: Any):", "        super().__init__(**data)"]
    )
    code_parts.append(f"        self._raw = _GeneratedClient(base_url=self.base_url)")
    code_parts.extend(client_inits)

    if top_level_method_definitions:
        # Ensure methods are indented correctly within the class
        indented_top_level_methods = [""]  # Start with a newline for separation
        for line in "\n".join(top_level_method_definitions).splitlines():
            indented_top_level_methods.append(f"    {line}" if line.strip() else "")
        code_parts.extend(indented_top_level_methods)

    code_parts.extend(
        [
            "\n",
            SDK_TEST_CODE_TEMPLATE.format(pkg_name=pkg_name, sdk_class=sdk_class_name),
        ]
    )
    return "\n".join(code_parts)


def main() -> None:
    p = argparse.ArgumentParser(description="Generate an SDK wrapper.")
    p.add_argument(
        "--package", required=True, help="root package name of the generated client"
    )
    p.add_argument(
        "--output", required=True, help="target .py file for the SDK wrapper"
    )
    p.add_argument("--class-name", default="WraperClient", help="wrapper class name")
    args = p.parse_args()
    code = render_wrapper(pkg_name=args.package, sdk_class_name=args.class_name)
    Path(args.output).write_text(code)
    print(f"✅  Wrote '{args.output}' with class '{args.class_name}'")


if __name__ == "__main__":
    main()
