from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.common import serialize, serialize_all
from api.store.team import TeamStore
from api.store.message import MessageStore
from _main_.utils.context import Context
from typing import Tuple

class TeamService:
  """
  Service Layer for all the teams
  """

  def __init__(self):
    self.store =  TeamStore()
    self.message_store = MessageStore()

  def get_team_info(self, context: Context, args) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.get_team_info(context, args)
    if err:
      return None, err
    return serialize(team, full=True), None

  def list_teams(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    team, err = self.store.list_teams(context, args)
    if err:
      return None, err
    return serialize_all(team), None

  def team_stats(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    stats, err = self.store.team_stats(context, args)
    if err:
      return None, err
    return stats, None


  def create_team(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.create_team(context, args)
    if err:
      return None, err

    # within store.create_team, an e-mail was sent to the community admin
    # 
    # TODO: the following functionality is needed
    # message to the effect that you have been named as a team admin
    #message_info, err = self.message_store.message_team_admin(context, args)
    #
    # message to community admins that a team was created (needs to be recorded in admin portal because the e-mail may be lost)
    #message_info, err = self.message_store.message_admin(context, args)

    return serialize(team), None


  def update_team(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.update_team(context, args)
    if err:
      return None, err
    return serialize(team), None

  def delete_team(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.delete_team(args)
    if err:
      return None, err
    return serialize(team), None

  def join_team(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.join_team(args)
    if err:
      return None, err
    return serialize(team), None

  def leave_team(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.leave_team(args)
    if err:
      return None, err
    return serialize(team), None

  def add_member(self, args) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.add_team_member(args)
    if err:
      return None, err
    return serialize(team), None

  def remove_team_member(self,args) -> Tuple[dict, MassEnergizeAPIError]:
    team, err = self.store.remove_team_member(args)
    if err:
      return None, err
    return serialize(team), None

  def members(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    members, err = self.store.members(context, args)
    if err:
      return None, err
    return serialize_all(members), None

  def members_preferred_names(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    preferred_names, err = self.store.members_preferred_names(context, args)
    if err:
      return None, err
    return preferred_names, None

  def message_admin(self, context, args) -> Tuple[dict, MassEnergizeAPIError]:
    message_info, err = self.message_store.message_team_admin(context, args)
    if err:
      return None, err
    return serialize(message_info), None


  def list_teams_for_community_admin(self, context:Context, args) -> Tuple[list, MassEnergizeAPIError]:
    teams, err = self.store.list_teams_for_community_admin(context, args)
    if err:
      return None, err
    return serialize_all(teams), None


  def list_teams_for_super_admin(self, context: Context) -> Tuple[list, MassEnergizeAPIError]:
    teams, err = self.store.list_teams_for_super_admin(context)
    if err:
      return None, err
    return serialize_all(teams), None


  def list_actions_completed(self, context: Context, args) -> Tuple[list, MassEnergizeAPIError]:
    completed_actions_list, err = self.store.list_actions_completed(context, args)
    if err:
      return None, err
    return completed_actions_list, None


