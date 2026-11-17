import asyncio
import inspect
import types
from copy import deepcopy
from typing import Any, Literal, Union, get_args, get_origin, get_type_hints
from unittest.mock import AsyncMock, create_autospec

import pytest

from lunia.adapters.napcat import api as api_module
from lunia.adapters.napcat.api import NapCatAPI
from lunia.adapters.napcat.client import NapCatClient
from tests import manual_napcat_cli

# 独立列出 108 个领域方法，防止遗漏、重复或归类漂移。
METHODS_BY_DOMAIN = {
    "message": [
        "group_poke",
        "friend_poke",
        "send_poke",
        "send_group_msg",
        "get_group_msg_history",
        "get_forward_msg",
        "get_friend_msg_history",
        "forward_friend_single_msg",
        "forward_group_single_msg",
        "mark_group_msg_as_read",
        "mark_private_msg_as_read",
        "get_msg",
        "send_private_msg",
        "send_msg",
        "delete_msg",
        "mark_msg_as_read",
        "_mark_all_as_read",
    ],
    "group": [
        "set_group_todo",
        "complete_group_todo",
        "cancel_group_todo",
        "del_group_album_media",
        "set_group_album_media_like",
        "cancel_group_album_media_like",
        "do_group_album_comment",
        "get_group_album_media_list",
        "get_qun_album_list",
        "upload_image_to_qun_album",
        "set_group_add_option",
        "set_group_robot_add_option",
        "set_group_search",
        "set_group_remark",
        "get_group_info_ex",
        "set_group_sign",
        "send_group_sign",
        "get_group_signed_list",
        "get_group_share_link",
        "upload_images_to_qun_album",
        "upload_video_to_qun_album",
        "get_group_detail_info",
        "get_group_list",
        "get_group_info",
        "get_group_member_list",
        "get_group_member_info",
        "set_group_add_request",
        "set_group_leave",
        "set_group_whole_ban",
        "set_group_ban",
        "set_group_kick",
        "set_group_admin",
        "set_group_name",
        "set_group_card",
        "get_essence_msg_list",
        "get_group_ignored_notifies",
        "delete_essence_msg",
        "_get_group_notice",
        "set_essence_msg",
        "_del_group_notice",
        "get_group_shut_list",
        "get_group_ignore_add_request",
        "set_group_member_invite_policy",
        "set_group_member_permissions",
        "set_group_new_member_history_visibility",
        "set_group_special_title",
        "get_group_honor_info",
        "_send_group_notice",
        "get_group_at_all_remain",
        "set_group_portrait",
    ],
    "user": [
        "set_self_longnick",
        "set_qq_avatar",
        "set_friend_remark",
        "send_like",
        "get_friend_list",
        "set_friend_add_request",
        "get_cookies",
        "get_recent_contact",
        "set_qq_profile",
        "delete_friend",
        "get_stranger_info",
        "_get_model_show",
        "get_friends_with_category",
        "get_profile_like",
        "set_diy_online_status",
        "get_unidirectional_friend_list",
    ],
    "file": [
        "get_file",
        "get_image",
        "get_record",
        "get_group_file_url",
        "get_private_file_url",
        "get_group_root_files",
        "download_file",
        "upload_group_file",
        "upload_private_file",
        "delete_group_file",
        "create_group_file_folder",
        "delete_group_folder",
        "get_group_file_system_info",
        "get_group_files_by_folder",
    ],
    "system": [
        "get_login_info",
        "get_version_info",
        "can_send_record",
        "can_send_image",
        "get_status",
        "set_online_status",
        "set_input_status",
        "nc_get_user_status",
        "check_url_safely",
    ],
    "extensions": ["ocr_image", "handle_quick_operation"],
}


def test_inventory_and_shared_client():
    client = create_autospec(NapCatClient, instance=True)
    api = NapCatAPI(client)
    expected = [name for names in METHODS_BY_DOMAIN.values() for name in names]
    assert len(expected) == len(set(expected)) == 108
    assert api_module.__all__ == ["NapCatAPI"]
    assert not inspect.getmembers(NapCatAPI, inspect.iscoroutinefunction)
    assert set(vars(api)) == {"client", *METHODS_BY_DOMAIN}
    assert set(manual_napcat_cli.get_methods(api)) == {
        f"{domain}.{name}"
        for domain, names in METHODS_BY_DOMAIN.items()
        for name in names
        if not name.startswith("_")
    }
    assert api.client is client

    for domain, names in METHODS_BY_DOMAIN.items():
        namespace = getattr(api, domain)
        assert namespace.client is client
        found = {
            name
            for name, _ in inspect.getmembers(
                type(namespace), inspect.iscoroutinefunction
            )
        }
        assert found == set(names)
        for name in names:
            assert not hasattr(api, name)
            method = getattr(namespace, name)
            assert method.__module__ == f"lunia.adapters.napcat.api.{domain}"
            assert inspect.signature(method).parameters["timeout"].default == 10.0


def sample_argument(annotation: Any) -> Any:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is Literal:
        return args[0]
    if origin in (Union, types.UnionType):
        return sample_argument(next(arg for arg in args if arg is not type(None)))
    if annotation is bool:
        return False
    if annotation is int:
        return 0
    if annotation is float:
        return 0.5
    if origin is list:
        return []
    if origin is dict:
        return {"test": "value"}
    return "test-value"


# 部分旧接口的必选条件由参数组合表达，而不是函数签名表达。
REQUIRED_OPTIONS = {
    "get_file": {"file": "example.txt"},
    "get_image": {"file": "example.png"},
    "get_record": {"file": "example.amr"},
    "get_forward_msg": {"id": "forward-id"},
    "mark_msg_as_read": {"message_id": "3"},
    "delete_friend": {"user_id": "2"},
    "download_file": {"url": "https://example.com/example.txt"},
    "do_group_album_comment": {"batch_id": "batch-id"},
    "send_msg": {"user_id": "2"},
    "create_group_file_folder": {"folder_name": "example"},
    "delete_group_folder": {"folder_id": "folder-id"},
    "get_group_files_by_folder": {"folder_id": "folder-id"},
}


@pytest.mark.parametrize(
    ("domain", "name"),
    [(domain, name) for domain, names in METHODS_BY_DOMAIN.items() for name in names],
    ids=[name for names in METHODS_BY_DOMAIN.values() for name in names],
)
def test_method_routes_to_shared_client(domain, name):
    client = create_autospec(NapCatClient, instance=True)
    response = {"status": "ok", "retcode": 0, "data": {"route": name}}
    client.call_api.return_value = response
    method = getattr(getattr(NapCatAPI(client), domain), name)
    hints = get_type_hints(method)
    required = {
        p.name: sample_argument(hints[p.name])
        for p in inspect.signature(method).parameters.values()
        if p.default is inspect.Parameter.empty
    }
    required.update(REQUIRED_OPTIONS.get(name, {}))

    assert asyncio.run(method(**required)) is response
    client.call_api.assert_awaited_once()
    assert client.call_api.await_args is not None
    expected_action = (
        ".handle_quick_operation" if name == "handle_quick_operation" else name
    )
    assert client.call_api.await_args.args[0] == expected_action
    assert client.call_api.await_args.kwargs == {"timeout": 10.0}


REQUEST_CASES = [
    pytest.param(
        "group",
        "set_group_todo",
        ("10",),
        {"message_seq": "0"},
        "set_group_todo",
        {"group_id": "10", "message_seq": "0"},
        10.0,
        id="group-todo-set",
    ),
    pytest.param(
        "group",
        "complete_group_todo",
        ("10",),
        {"message_id": "3"},
        "complete_group_todo",
        {"group_id": "10", "message_id": "3"},
        10.0,
        id="group-todo-complete",
    ),
    pytest.param(
        "group",
        "cancel_group_todo",
        ("10",),
        {},
        "cancel_group_todo",
        {"group_id": "10"},
        10.0,
        id="group-todo-cancel",
    ),
    pytest.param(
        "message",
        "group_poke",
        ("10", "2"),
        {"target_id": "3"},
        "group_poke",
        {"group_id": "10", "user_id": "2", "target_id": "3"},
        10.0,
        id="message-group-poke",
    ),
    pytest.param(
        "message",
        "friend_poke",
        ("2",),
        {},
        "friend_poke",
        {"user_id": "2"},
        10.0,
        id="message-friend-poke",
    ),
    pytest.param(
        "message",
        "send_poke",
        ("2",),
        {"group_id": "10", "timeout": None},
        "send_poke",
        {"user_id": "2", "group_id": "10"},
        None,
        id="message-poke",
    ),
    pytest.param(
        "message",
        "send_group_msg",
        ("10", [{"type": "text", "data": {"text": "hi"}}]),
        {
            "auto_escape": False,
            "source": "",
            "news": [],
            "summary": "",
            "prompt": "",
            "send_timeout_ms": 0,
            "timeout": 1.5,
        },
        "send_group_msg",
        {
            "group_id": "10",
            "message": [{"type": "text", "data": {"text": "hi"}}],
            "auto_escape": False,
            "source": "",
            "news": [],
            "summary": "",
            "prompt": "",
            "timeout": 0,
        },
        1.5,
        id="message-falsy-fields-and-two-timeouts",
    ),
    pytest.param(
        "message",
        "send_private_msg",
        ("2", "hi", 0.5),
        {"group_id": "10"},
        "send_private_msg",
        {"user_id": "2", "message": "hi", "group_id": "10"},
        0.5,
        id="private-positional-timeout",
    ),
    pytest.param(
        "message",
        "get_group_msg_history",
        ("10",),
        {"message_seq": "0"},
        "get_group_msg_history",
        {
            "group_id": "10",
            "message_seq": "0",
            "count": 20,
            "reverse_order": False,
            "reverseOrder": False,
            "disable_get_url": False,
            "parse_mult_msg": True,
            "quick_reply": False,
        },
        10.0,
        id="history-compatibility-fields",
    ),
    pytest.param(
        "message",
        "get_forward_msg",
        (),
        {"id": "a", "message_id": "b"},
        "get_forward_msg",
        {"id": "a", "message_id": "b"},
        10.0,
        id="forward-both-id-aliases",
    ),
    pytest.param(
        "group",
        "get_group_member_info",
        ("10", "2"),
        {"no_cache": False},
        "get_group_member_info",
        {"group_id": "10", "user_id": "2", "no_cache": False},
        10.0,
        id="group-member-existing-wrapper",
    ),
    pytest.param(
        "group",
        "set_group_member_permissions",
        ("10",),
        {"allow_member_upload_album": False},
        "set_group_member_permissions",
        {"group_id": "10", "allow_member_upload_album": False},
        10.0,
        id="group-false-permission",
    ),
    pytest.param(
        "user",
        "get_stranger_info",
        ("2",),
        {},
        "get_stranger_info",
        {"user_id": "2", "no_cache": False},
        10.0,
        id="user-default-no-cache",
    ),
    pytest.param(
        "user",
        "delete_friend",
        (),
        {"friend_id": "2", "user_id": "2", "temp_block": False, "temp_both_del": False},
        "delete_friend",
        {"friend_id": "2", "user_id": "2", "temp_block": False, "temp_both_del": False},
        10.0,
        id="friend-id-aliases-and-false-flags",
    ),
    pytest.param(
        "user",
        "_get_model_show",
        (),
        {},
        "_get_model_show",
        {},
        10.0,
        id="private-compatibility-method",
    ),
    pytest.param(
        "file",
        "get_file",
        (),
        {"file_id": "file-1"},
        "get_file",
        {"file_id": "file-1"},
        10.0,
        id="file-none-omission",
    ),
    pytest.param(
        "file",
        "delete_group_file",
        ("10", "file-1"),
        {"bus_id": 0, "busid": 0},
        "delete_group_file",
        {"group_id": "10", "file_id": "file-1", "bus_id": 0, "busid": 0},
        10.0,
        id="file-bus-id-aliases",
    ),
    pytest.param(
        "file",
        "upload_group_file",
        ("10", "example.txt", "example.txt"),
        {"folder": "", "folder_id": "", "upload_file": False},
        "upload_group_file",
        {
            "group_id": "10",
            "file": "example.txt",
            "name": "example.txt",
            "folder": "",
            "folder_id": "",
            "upload_file": False,
        },
        10.0,
        id="file-folder-aliases",
    ),
    pytest.param(
        "system",
        "set_online_status",
        ("10", "0", "0"),
        {},
        "set_online_status",
        {"status": "10", "ext_status": "0", "battery_status": "0"},
        10.0,
        id="system-string-status",
    ),
    pytest.param(
        "extensions",
        "handle_quick_operation",
        ({"post_type": "message"}, {"reply": "hi"}),
        {},
        ".handle_quick_operation",
        {"context": {"post_type": "message"}, "operation": {"reply": "hi"}},
        10.0,
        id="quick-operation-dot-action",
    ),
    pytest.param(
        "extensions",
        "ocr_image",
        ("example.png",),
        {},
        "ocr_image",
        {"image": "example.png"},
        10.0,
        id="ocr-extension",
    ),
]


@pytest.mark.parametrize(
    ("domain", "name", "args", "kwargs", "action", "params", "timeout"),
    REQUEST_CASES,
)
def test_request_construction(domain, name, args, kwargs, action, params, timeout):
    client = create_autospec(NapCatClient, instance=True)
    response = {"status": "failed", "retcode": 1400, "data": None, "extra": "unchanged"}
    client.call_api.return_value = response
    api = NapCatAPI(client)
    owner = getattr(api, domain)
    original = deepcopy((args, kwargs))

    assert asyncio.run(getattr(owner, name)(*args, **kwargs)) is response
    client.call_api.assert_awaited_once_with(action, params, timeout=timeout)
    assert (args, kwargs) == original


@pytest.mark.parametrize(
    ("domain", "name", "kwargs"),
    [
        ("file", "get_file", {}),
        ("file", "get_image", {}),
        ("file", "get_record", {"out_format": "mp3"}),
        ("message", "get_forward_msg", {}),
        ("message", "mark_msg_as_read", {}),
        ("message", "send_msg", {"message_type": "private", "message": "hi"}),
        ("message", "send_msg", {"message_type": "group", "message": "hi"}),
        ("message", "send_msg", {"message_type": "invalid", "message": "hi"}),
        ("user", "delete_friend", {}),
        ("file", "download_file", {}),
        ("file", "create_group_file_folder", {"group_id": "10"}),
        ("file", "delete_group_folder", {"group_id": "10"}),
        ("file", "get_group_files_by_folder", {"group_id": "10"}),
        (
            "group",
            "do_group_album_comment",
            {"group_id": "10", "album_id": "a", "content": "hi"},
        ),
    ],
)
def test_existing_argument_validation(domain, name, kwargs):
    client = create_autospec(NapCatClient, instance=True)
    api = NapCatAPI(client)
    owner = getattr(api, domain)
    with pytest.raises(ValueError):
        asyncio.run(getattr(owner, name)(**kwargs))
    client.call_api.assert_not_awaited()


def test_console_executes_qualified_read_only_method(monkeypatch):
    client = create_autospec(NapCatClient, instance=True)
    api = NapCatAPI(client)
    ask = AsyncMock(side_effect=["3", ""])
    monkeypatch.setattr(manual_napcat_cli, "ask", ask)

    asyncio.run(manual_napcat_cli.execute(api, "message.get_msg"))

    assert ask.await_count == 2
    client.call_api.assert_awaited_once_with("get_msg", {"message_id": 3}, timeout=10.0)


@pytest.mark.parametrize("answer", ["y", "n"])
def test_console_preserves_confirmation_for_writes(answer, monkeypatch):
    client = create_autospec(NapCatClient, instance=True)
    api = NapCatAPI(client)

    async def respond(prompt: str) -> str:
        if prompt.startswith("  group_id"):
            return '"10"'
        if prompt.startswith("  message"):
            return '"hi"'
        if "确认执行" in prompt:
            return answer
        return ""

    ask = AsyncMock(side_effect=respond)
    monkeypatch.setattr(manual_napcat_cli, "ask", ask)
    asyncio.run(manual_napcat_cli.execute(api, "message.send_group_msg"))

    assert "确认执行" in ask.await_args_list[-1].args[0]
    if answer == "y":
        client.call_api.assert_awaited_once_with(
            "send_group_msg", {"group_id": "10", "message": "hi"}, timeout=10.0
        )
    else:
        client.call_api.assert_not_awaited()
