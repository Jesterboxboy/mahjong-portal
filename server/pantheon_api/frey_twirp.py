# -*- coding: utf-8 -*-
# Generated by https://github.com/verloop/twirpy/protoc-gen-twirpy.  DO NOT EDIT!
# source: frey.proto

from google.protobuf import symbol_database as _symbol_database
from twirp.base import Endpoint
from twirp.client import TwirpClient
from twirp.server import TwirpServer

_sym_db = _symbol_database.Default()


class FreyServer(TwirpServer):
    def __init__(self, *args, service, server_path_prefix="/twirp"):
        super().__init__(service=service)
        self._prefix = f"{server_path_prefix}/Common.Frey"
        self._endpoints = {
            "RequestRegistration": Endpoint(
                service_name="Frey",
                name="RequestRegistration",
                function=getattr(service, "RequestRegistration"),
                input=_sym_db.GetSymbol("Common.Auth_RequestRegistration_Payload"),
                output=_sym_db.GetSymbol("Common.Auth_RequestRegistration_Response"),
            ),
            "ApproveRegistration": Endpoint(
                service_name="Frey",
                name="ApproveRegistration",
                function=getattr(service, "ApproveRegistration"),
                input=_sym_db.GetSymbol("Common.Auth_ApproveRegistration_Payload"),
                output=_sym_db.GetSymbol("Common.Auth_ApproveRegistration_Response"),
            ),
            "Authorize": Endpoint(
                service_name="Frey",
                name="Authorize",
                function=getattr(service, "Authorize"),
                input=_sym_db.GetSymbol("Common.Auth_Authorize_Payload"),
                output=_sym_db.GetSymbol("Common.Auth_Authorize_Response"),
            ),
            "QuickAuthorize": Endpoint(
                service_name="Frey",
                name="QuickAuthorize",
                function=getattr(service, "QuickAuthorize"),
                input=_sym_db.GetSymbol("Common.Auth_QuickAuthorize_Payload"),
                output=_sym_db.GetSymbol("Common.Auth_QuickAuthorize_Response"),
            ),
            "Me": Endpoint(
                service_name="Frey",
                name="Me",
                function=getattr(service, "Me"),
                input=_sym_db.GetSymbol("Common.Auth_Me_Payload"),
                output=_sym_db.GetSymbol("Common.Auth_Me_Response"),
            ),
            "ChangePassword": Endpoint(
                service_name="Frey",
                name="ChangePassword",
                function=getattr(service, "ChangePassword"),
                input=_sym_db.GetSymbol("Common.Auth_ChangePassword_Payload"),
                output=_sym_db.GetSymbol("Common.Auth_ChangePassword_Response"),
            ),
            "RequestResetPassword": Endpoint(
                service_name="Frey",
                name="RequestResetPassword",
                function=getattr(service, "RequestResetPassword"),
                input=_sym_db.GetSymbol("Common.Auth_RequestResetPassword_Payload"),
                output=_sym_db.GetSymbol("Common.Auth_RequestResetPassword_Response"),
            ),
            "ApproveResetPassword": Endpoint(
                service_name="Frey",
                name="ApproveResetPassword",
                function=getattr(service, "ApproveResetPassword"),
                input=_sym_db.GetSymbol("Common.Auth_ApproveResetPassword_Payload"),
                output=_sym_db.GetSymbol("Common.Auth_ApproveResetPassword_Response"),
            ),
            "GetAccessRules": Endpoint(
                service_name="Frey",
                name="GetAccessRules",
                function=getattr(service, "GetAccessRules"),
                input=_sym_db.GetSymbol("Common.Access_GetAccessRules_Payload"),
                output=_sym_db.GetSymbol("Common.Access_GetAccessRules_Response"),
            ),
            "GetRuleValue": Endpoint(
                service_name="Frey",
                name="GetRuleValue",
                function=getattr(service, "GetRuleValue"),
                input=_sym_db.GetSymbol("Common.Access_GetRuleValue_Payload"),
                output=_sym_db.GetSymbol("Common.Access_GetRuleValue_Response"),
            ),
            "UpdatePersonalInfo": Endpoint(
                service_name="Frey",
                name="UpdatePersonalInfo",
                function=getattr(service, "UpdatePersonalInfo"),
                input=_sym_db.GetSymbol("Common.Persons_UpdatePersonalInfo_Payload"),
                output=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            ),
            "GetPersonalInfo": Endpoint(
                service_name="Frey",
                name="GetPersonalInfo",
                function=getattr(service, "GetPersonalInfo"),
                input=_sym_db.GetSymbol("Common.Persons_GetPersonalInfo_Payload"),
                output=_sym_db.GetSymbol("Common.Persons_GetPersonalInfo_Response"),
            ),
            "FindByTenhouIds": Endpoint(
                service_name="Frey",
                name="FindByTenhouIds",
                function=getattr(service, "FindByTenhouIds"),
                input=_sym_db.GetSymbol("Common.Persons_FindByTenhouIds_Payload"),
                output=_sym_db.GetSymbol("Common.Persons_FindByTenhouIds_Response"),
            ),
            "FindByTitle": Endpoint(
                service_name="Frey",
                name="FindByTitle",
                function=getattr(service, "FindByTitle"),
                input=_sym_db.GetSymbol("Common.Persons_FindByTitle_Payload"),
                output=_sym_db.GetSymbol("Common.Persons_FindByTitle_Response"),
            ),
            "GetGroups": Endpoint(
                service_name="Frey",
                name="GetGroups",
                function=getattr(service, "GetGroups"),
                input=_sym_db.GetSymbol("Common.Persons_GetGroups_Payload"),
                output=_sym_db.GetSymbol("Common.Persons_GetGroups_Response"),
            ),
            "GetEventAdmins": Endpoint(
                service_name="Frey",
                name="GetEventAdmins",
                function=getattr(service, "GetEventAdmins"),
                input=_sym_db.GetSymbol("Common.Access_GetEventAdmins_Payload"),
                output=_sym_db.GetSymbol("Common.Access_GetEventAdmins_Response"),
            ),
            "GetSuperadminFlag": Endpoint(
                service_name="Frey",
                name="GetSuperadminFlag",
                function=getattr(service, "GetSuperadminFlag"),
                input=_sym_db.GetSymbol("Common.Access_GetSuperadminFlag_Payload"),
                output=_sym_db.GetSymbol("Common.Access_GetSuperadminFlag_Response"),
            ),
            "GetOwnedEventIds": Endpoint(
                service_name="Frey",
                name="GetOwnedEventIds",
                function=getattr(service, "GetOwnedEventIds"),
                input=_sym_db.GetSymbol("Common.Access_GetOwnedEventIds_Payload"),
                output=_sym_db.GetSymbol("Common.Access_GetOwnedEventIds_Response"),
            ),
            "GetRulesList": Endpoint(
                service_name="Frey",
                name="GetRulesList",
                function=getattr(service, "GetRulesList"),
                input=_sym_db.GetSymbol("Common.Access_GetRulesList_Payload"),
                output=_sym_db.GetSymbol("Common.Access_GetRulesList_Response"),
            ),
            "GetAllEventRules": Endpoint(
                service_name="Frey",
                name="GetAllEventRules",
                function=getattr(service, "GetAllEventRules"),
                input=_sym_db.GetSymbol("Common.Access_GetAllEventRules_Payload"),
                output=_sym_db.GetSymbol("Common.Access_GetAllEventRules_Response"),
            ),
            "GetPersonAccess": Endpoint(
                service_name="Frey",
                name="GetPersonAccess",
                function=getattr(service, "GetPersonAccess"),
                input=_sym_db.GetSymbol("Common.Access_GetPersonAccess_Payload"),
                output=_sym_db.GetSymbol("Common.Access_GetPersonAccess_Response"),
            ),
            "GetGroupAccess": Endpoint(
                service_name="Frey",
                name="GetGroupAccess",
                function=getattr(service, "GetGroupAccess"),
                input=_sym_db.GetSymbol("Common.Access_GetGroupAccess_Payload"),
                output=_sym_db.GetSymbol("Common.Access_GetGroupAccess_Response"),
            ),
            "GetAllPersonAccess": Endpoint(
                service_name="Frey",
                name="GetAllPersonAccess",
                function=getattr(service, "GetAllPersonAccess"),
                input=_sym_db.GetSymbol("Common.Access_GetAllPersonAccess_Payload"),
                output=_sym_db.GetSymbol("Common.Access_GetAllPersonAccess_Response"),
            ),
            "GetAllGroupAccess": Endpoint(
                service_name="Frey",
                name="GetAllGroupAccess",
                function=getattr(service, "GetAllGroupAccess"),
                input=_sym_db.GetSymbol("Common.Access_GetAllGroupAccess_Payload"),
                output=_sym_db.GetSymbol("Common.Access_GetAllGroupAccess_Response"),
            ),
            "AddRuleForPerson": Endpoint(
                service_name="Frey",
                name="AddRuleForPerson",
                function=getattr(service, "AddRuleForPerson"),
                input=_sym_db.GetSymbol("Common.Access_AddRuleForPerson_Payload"),
                output=_sym_db.GetSymbol("Common.Access_AddRuleForPerson_Response"),
            ),
            "AddRuleForGroup": Endpoint(
                service_name="Frey",
                name="AddRuleForGroup",
                function=getattr(service, "AddRuleForGroup"),
                input=_sym_db.GetSymbol("Common.Access_AddRuleForGroup_Payload"),
                output=_sym_db.GetSymbol("Common.Access_AddRuleForGroup_Response"),
            ),
            "UpdateRuleForPerson": Endpoint(
                service_name="Frey",
                name="UpdateRuleForPerson",
                function=getattr(service, "UpdateRuleForPerson"),
                input=_sym_db.GetSymbol("Common.Access_UpdateRuleForPerson_Payload"),
                output=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            ),
            "UpdateRuleForGroup": Endpoint(
                service_name="Frey",
                name="UpdateRuleForGroup",
                function=getattr(service, "UpdateRuleForGroup"),
                input=_sym_db.GetSymbol("Common.Access_UpdateRuleForGroup_Payload"),
                output=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            ),
            "DeleteRuleForPerson": Endpoint(
                service_name="Frey",
                name="DeleteRuleForPerson",
                function=getattr(service, "DeleteRuleForPerson"),
                input=_sym_db.GetSymbol("Common.Access_DeleteRuleForPerson_Payload"),
                output=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            ),
            "DeleteRuleForGroup": Endpoint(
                service_name="Frey",
                name="DeleteRuleForGroup",
                function=getattr(service, "DeleteRuleForGroup"),
                input=_sym_db.GetSymbol("Common.Access_DeleteRuleForGroup_Payload"),
                output=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            ),
            "ClearAccessCache": Endpoint(
                service_name="Frey",
                name="ClearAccessCache",
                function=getattr(service, "ClearAccessCache"),
                input=_sym_db.GetSymbol("Common.Access_ClearAccessCache_Payload"),
                output=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            ),
            "CreateAccount": Endpoint(
                service_name="Frey",
                name="CreateAccount",
                function=getattr(service, "CreateAccount"),
                input=_sym_db.GetSymbol("Common.Persons_CreateAccount_Payload"),
                output=_sym_db.GetSymbol("Common.Persons_CreateAccount_Response"),
            ),
            "CreateGroup": Endpoint(
                service_name="Frey",
                name="CreateGroup",
                function=getattr(service, "CreateGroup"),
                input=_sym_db.GetSymbol("Common.Persons_CreateGroup_Payload"),
                output=_sym_db.GetSymbol("Common.Persons_CreateGroup_Response"),
            ),
            "UpdateGroup": Endpoint(
                service_name="Frey",
                name="UpdateGroup",
                function=getattr(service, "UpdateGroup"),
                input=_sym_db.GetSymbol("Common.Persons_UpdateGroup_Payload"),
                output=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            ),
            "DeleteGroup": Endpoint(
                service_name="Frey",
                name="DeleteGroup",
                function=getattr(service, "DeleteGroup"),
                input=_sym_db.GetSymbol("Common.Persons_DeleteGroup_Payload"),
                output=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            ),
            "AddPersonToGroup": Endpoint(
                service_name="Frey",
                name="AddPersonToGroup",
                function=getattr(service, "AddPersonToGroup"),
                input=_sym_db.GetSymbol("Common.Persons_AddPersonToGroup_Payload"),
                output=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            ),
            "RemovePersonFromGroup": Endpoint(
                service_name="Frey",
                name="RemovePersonFromGroup",
                function=getattr(service, "RemovePersonFromGroup"),
                input=_sym_db.GetSymbol("Common.Persons_RemovePersonFromGroup_Payload"),
                output=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            ),
            "GetPersonsOfGroup": Endpoint(
                service_name="Frey",
                name="GetPersonsOfGroup",
                function=getattr(service, "GetPersonsOfGroup"),
                input=_sym_db.GetSymbol("Common.Persons_GetPersonsOfGroup_Payload"),
                output=_sym_db.GetSymbol("Common.Persons_GetPersonsOfGroup_Response"),
            ),
            "GetGroupsOfPerson": Endpoint(
                service_name="Frey",
                name="GetGroupsOfPerson",
                function=getattr(service, "GetGroupsOfPerson"),
                input=_sym_db.GetSymbol("Common.Persons_GetGroupsOfPerson_Payload"),
                output=_sym_db.GetSymbol("Common.Persons_GetGroupsOfPerson_Response"),
            ),
            "AddSystemWideRuleForPerson": Endpoint(
                service_name="Frey",
                name="AddSystemWideRuleForPerson",
                function=getattr(service, "AddSystemWideRuleForPerson"),
                input=_sym_db.GetSymbol("Common.Access_AddSystemWideRuleForPerson_Payload"),
                output=_sym_db.GetSymbol("Common.Access_AddSystemWideRuleForPerson_Response"),
            ),
            "AddSystemWideRuleForGroup": Endpoint(
                service_name="Frey",
                name="AddSystemWideRuleForGroup",
                function=getattr(service, "AddSystemWideRuleForGroup"),
                input=_sym_db.GetSymbol("Common.Access_AddSystemWideRuleForGroup_Payload"),
                output=_sym_db.GetSymbol("Common.Access_AddSystemWideRuleForGroup_Response"),
            ),
        }


class FreyClient(TwirpClient):
    def RequestRegistration(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/RequestRegistration",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Auth_RequestRegistration_Response"),
            **kwargs,
        )

    def ApproveRegistration(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/ApproveRegistration",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Auth_ApproveRegistration_Response"),
            **kwargs,
        )

    def Authorize(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/Authorize",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Auth_Authorize_Response"),
            **kwargs,
        )

    def QuickAuthorize(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/QuickAuthorize",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Auth_QuickAuthorize_Response"),
            **kwargs,
        )

    def Me(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/Me",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Auth_Me_Response"),
            **kwargs,
        )

    def ChangePassword(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/ChangePassword",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Auth_ChangePassword_Response"),
            **kwargs,
        )

    def RequestResetPassword(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/RequestResetPassword",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Auth_RequestResetPassword_Response"),
            **kwargs,
        )

    def ApproveResetPassword(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/ApproveResetPassword",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Auth_ApproveResetPassword_Response"),
            **kwargs,
        )

    def GetAccessRules(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetAccessRules",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_GetAccessRules_Response"),
            **kwargs,
        )

    def GetRuleValue(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetRuleValue",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_GetRuleValue_Response"),
            **kwargs,
        )

    def UpdatePersonalInfo(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/UpdatePersonalInfo",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            **kwargs,
        )

    def GetPersonalInfo(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetPersonalInfo",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Persons_GetPersonalInfo_Response"),
            **kwargs,
        )

    def FindByTenhouIds(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/FindByTenhouIds",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Persons_FindByTenhouIds_Response"),
            **kwargs,
        )

    def FindByTitle(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/FindByTitle",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Persons_FindByTitle_Response"),
            **kwargs,
        )

    def GetGroups(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetGroups",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Persons_GetGroups_Response"),
            **kwargs,
        )

    def GetEventAdmins(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetEventAdmins",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_GetEventAdmins_Response"),
            **kwargs,
        )

    def GetSuperadminFlag(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetSuperadminFlag",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_GetSuperadminFlag_Response"),
            **kwargs,
        )

    def GetOwnedEventIds(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetOwnedEventIds",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_GetOwnedEventIds_Response"),
            **kwargs,
        )

    def GetRulesList(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetRulesList",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_GetRulesList_Response"),
            **kwargs,
        )

    def GetAllEventRules(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetAllEventRules",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_GetAllEventRules_Response"),
            **kwargs,
        )

    def GetPersonAccess(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetPersonAccess",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_GetPersonAccess_Response"),
            **kwargs,
        )

    def GetGroupAccess(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetGroupAccess",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_GetGroupAccess_Response"),
            **kwargs,
        )

    def GetAllPersonAccess(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetAllPersonAccess",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_GetAllPersonAccess_Response"),
            **kwargs,
        )

    def GetAllGroupAccess(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetAllGroupAccess",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_GetAllGroupAccess_Response"),
            **kwargs,
        )

    def AddRuleForPerson(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/AddRuleForPerson",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_AddRuleForPerson_Response"),
            **kwargs,
        )

    def AddRuleForGroup(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/AddRuleForGroup",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_AddRuleForGroup_Response"),
            **kwargs,
        )

    def UpdateRuleForPerson(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/UpdateRuleForPerson",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            **kwargs,
        )

    def UpdateRuleForGroup(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/UpdateRuleForGroup",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            **kwargs,
        )

    def DeleteRuleForPerson(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/DeleteRuleForPerson",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            **kwargs,
        )

    def DeleteRuleForGroup(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/DeleteRuleForGroup",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            **kwargs,
        )

    def ClearAccessCache(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/ClearAccessCache",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            **kwargs,
        )

    def CreateAccount(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/CreateAccount",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Persons_CreateAccount_Response"),
            **kwargs,
        )

    def CreateGroup(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/CreateGroup",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Persons_CreateGroup_Response"),
            **kwargs,
        )

    def UpdateGroup(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/UpdateGroup",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            **kwargs,
        )

    def DeleteGroup(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/DeleteGroup",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            **kwargs,
        )

    def AddPersonToGroup(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/AddPersonToGroup",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            **kwargs,
        )

    def RemovePersonFromGroup(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/RemovePersonFromGroup",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Generic_Success_Response"),
            **kwargs,
        )

    def GetPersonsOfGroup(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetPersonsOfGroup",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Persons_GetPersonsOfGroup_Response"),
            **kwargs,
        )

    def GetGroupsOfPerson(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/GetGroupsOfPerson",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Persons_GetGroupsOfPerson_Response"),
            **kwargs,
        )

    def AddSystemWideRuleForPerson(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/AddSystemWideRuleForPerson",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_AddSystemWideRuleForPerson_Response"),
            **kwargs,
        )

    def AddSystemWideRuleForGroup(self, *args, ctx, request, server_path_prefix="/twirp", **kwargs):
        return self._make_request(
            url=f"{server_path_prefix}/Common.Frey/AddSystemWideRuleForGroup",
            ctx=ctx,
            request=request,
            response_obj=_sym_db.GetSymbol("Common.Access_AddSystemWideRuleForGroup_Response"),
            **kwargs,
        )
