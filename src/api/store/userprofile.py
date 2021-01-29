from database.models import UserProfile, CommunityMember, EventAttendee, RealEstateUnit, Location, UserActionRel, Vendor, Action, Data, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.context import Context
from django.db.models import F
from sentry_sdk import capture_message
from .utils import get_community, get_user, get_user_or_die, get_community_or_die, get_admin_communities, remove_dups

class UserStore:
  def __init__(self):
    self.name = "UserProfile Store/DB"


  def _has_access(self, context: Context, user_id=None, email=None):
    """
    Checks to make sure if the user has access to the user profile they want to 
    access
    """
    if (not user_id and not email):
      return False

    if not context.user_is_logged_in:
      return False

    if context.user_is_admin():
      # TODO: update this to only super admins.  Do specific checks for 
      # community admins to make sure user is in their community first
      return True
    
    if user_id and (context.user_id == user_id):
      return True 
    
    if email and (context.user_email == email):
      return True 
    
    return False 

  def get_user_info(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      email = args.get('email', None)
      user_id = args.get('user_id', None)

      # if not self._has_access(context, user_id, email):
      #   return None, CustomMassenergizeError("permission_denied")

      user = get_user_or_die(context, args)
      return user, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))


  def remove_household(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      household_id = args.get('household_id', None) or args.get('household_id', None)
      if not household_id:
        return None, CustomMassenergizeError("Please provide household_id")

      return RealEstateUnit.objects.get(pk=household_id).delete(), None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))

  def add_household(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      user = get_user_or_die(context, args)
      name = args.pop('name', None)
      unit_type=args.pop('unit_type', None)
      # Location is string address of the unit, deliminted as follows:
      # 'street' + ", " + city + ", " + state + ", " + 'zipcode'
      location=args.pop('location', None)
      address = args.pop('address', None)
      if address:
        street = address.get('street', None)
        unit_number = address.get('unit_number', None)
        zipcode = address.get('zipcode', None)
        city = address.get('city', None)
        county = address.get('county', None)
        state = address.get('state', None)
      else:
        # get address from location string
        loc_parts = location.split(', ')
        street = unit_number = city = county = state = zipcode = None
        if len(loc_parts)>= 4:
          street = loc_parts[0]
          unit_number = None
          city = loc_parts[1]
          county = None
          state = loc_parts[2]
          zipcode = loc_parts[3]

      location_type = 'FULL_ADDRESS'
      if zipcode and not street and not city and not county and not state:
        location_type = 'ZIP_CODE_ONLY'
      elif state and not zipcode and not city and not county:
        location_type = 'STATE_ONLY'
      elif city and not street:
        location_type = 'CITY_ONLY'
      elif county and not city:
        location_type = 'COUNTY_ONLY'

      newloc = Location.objects.get_or_create(
          location_type = location_type,
          street = street,
          unit_number = unit_number,
          zipcode = zipcode,
          city = city,
          county = county,
          state = state
      )

      # this is currently a bogus community, the one signed into when the profile was created
      # communityId = args.pop('community_id', None) or args.pop('community', None) 
      communityId = None

      # determine which, if any, community this household is actually in
      communities = Community.objects.filter(deleted=False, is_geographically_focused=True)
      community_found = False
      for community in communities:
        cid = community.id
        for loc in community.zipcodes:
          if loc.zipcode == zipcode:
            # this is the one
            community_found = True
            communityId = cid
            break
        if community_found:
          break

      new_unit = RealEstateUnit.objects.create(name=name, unit_type=unit_type,location=location)
      new_unit.save()

      new_unit.address = newloc

      user.real_estate_units.add(new_unit)
      if community_found:
        #community = Community.objects.get(id=communityId)
        new_unit.community = community
      else:
        new_unit.community = None

      new_unit.save()

      return new_unit, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))

  def edit_household(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      user = get_user_or_die(context, args)
      name = args.pop('name', None)
      household_id = args.get('household_id', None)
      unit_type=args.pop('unit_type', None)
      location=args.pop('location', None)
      # this address location now will contain the parsed address      
      address = args.pop('address', None)
      if address:
        street = address.get('street', None)
        unit_number = address.get('unit_number', None)
        zipcode = address.get('zipcode', None)
        city = address.get('city', None)
        county = address.get('county', None)
        state = address.get('state', None)
      else:
        # get address from location string
        loc_parts = location.split(', ')
        street = unit_number = city = county = state = zipcode = None
        if len(loc_parts)>= 4:
          street = loc_parts[0]
          unit_number = None
          city = loc_parts[1]
          county = None
          state = loc_parts[2]
          zipcode = loc_parts[3]

      location_type = 'FULL_ADDRESS'
      if zipcode and not street and not city and not county and not state:
        location_type = 'ZIP_CODE_ONLY'
      elif state and not zipcode and not city and not county:
        location_type = 'STATE_ONLY'
      elif city and not street:
        location_type = 'CITY_ONLY'
      elif county and not city:
        location_type = 'COUNTY_ONLY'

      # this is currently a bogus community, the one signed into when the profile was created
      # communityId = args.pop('community_id', None) or args.pop('community', None) 
      communityId = None 

      # determine which, if any, community this household is actually in
      communities = Community.objects.filter(deleted=False, is_geographically_focused=True)
      community_found = False
      for community in communities:
        cid = community.id
        for loc in community.zipcodes:
          if loc.zipcode == zipcode:
            # this is the one
            community_found = True
            communityId = cid
            break
        if community_found:
          break

      if not household_id:
        return None, CustomMassenergizeError("Please provide household_id")

      new_unit = RealEstateUnit.objects.get(pk=household_id)
      new_unit.name = name
      new_unit.unit_type = unit_type
      new_unit.location = location

      if community_found:
        # community = Community.objects.get(id=communityId)
        new_unit.community = community
      else:
        new_unit.community = None

      newloc = new_unit.address
      if newloc:
        newloc.location_type = location_type,
        newloc.street = street,
        newloc.unit_number = unit_number,
        newloc.zipcode = zipcode,
        newloc.city = city,
        newloc.county = county,
        newloc.state = state
        newloc.save()      
      else:
        newloc, created = Location.objects.get_or_create(
          location_type = location_type,
          street = street,
          unit_number = unit_number,
          zipcode = zipcode,
          city = city,
          county = county,
          state = state
      ) 

      new_unit.address = newloc

      new_unit.save()

      return new_unit, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))

  def list_households(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      user = get_user_or_die(context, args)

      return user.real_estate_units.all(), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))

  def list_users(self, community_id) -> (list, MassEnergizeAPIError):
    community,err = get_community(community_id)
    
    if not community:
      return [], None
    return community.userprofile_set.all(), None

  def list_events_for_user(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      user = get_user_or_die(context, args)
      if not user:
        return []
      return EventAttendee.objects.filter(attendee=user), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def create_user(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:

      email = args.get('email', None) 
      community = get_community_or_die(context, args)


      # allow home address to be passed in
      location = args.pop('location', '')

      if not email:
        return None, CustomMassenergizeError("email required for sign up")
      
      user = UserProfile.objects.filter(email=email).first()
      if not user:
        new_user: UserProfile = UserProfile.objects.create(
          full_name = args.get('full_name'), 
          preferred_name = args.get('preferred_name', None), 
          email = args.get('email'), 
          is_vendor = args.get('is_vendor', False), 
          accepts_terms_and_conditions = args.pop('accepts_terms_and_conditions', False)
        )
      else:
        new_user: UserProfile = user


      community_member_exists = CommunityMember.objects.filter(user=new_user, community=community).exists()
      if not community_member_exists:
        # add them as a member to community 
        CommunityMember.objects.create(user=new_user, community=community)

        #create their first household
        household = RealEstateUnit.objects.create(name="Home", unit_type="residential", community=community, location=location)
        new_user.real_estate_units.add(household)
    
      
      res = {
        "user": new_user,
        "community": community
      }
      return res, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def update_user(self, context: Context, user_id, args) -> (dict, MassEnergizeAPIError):
    try:
      email = args.get('email', None)
      # user_id = args.get('user_id', None)

      if not self._has_access(context, user_id, email):
        return None, CustomMassenergizeError("permission_denied")

      if context.user_is_logged_in and ((context.user_id == user_id) or (context.user_is_admin())):
        user = UserProfile.objects.filter(id=user_id)
        if not user:
          return None, InvalidResourceError()

        user.update(**args)
        return user.first(), None
      else:
        return None, CustomMassenergizeError('permission_denied')

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def delete_user(self, context: Context, user_id) -> (dict, MassEnergizeAPIError):
    try:
      if not user_id:
        return None, InvalidResourceError()

      #check to make sure the one deleting is an admin
      if not context.user_is_admin():

        # if they are not an admin make sure they can only delete themselves
        if not context.user_id != user_id:
          return None, NotAuthorizedError()

      users = UserProfile.objects.filter(id=user_id)
      users.update(is_deleted=True)
      return users.first(), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_users_for_community_admin(self,  context: Context, community_id) -> (list, MassEnergizeAPIError):
    try:
      if context.user_is_super_admin:
        return self.list_users_for_super_admin(context)

      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()

      community, err = get_community(community_id)

      if not community and context.user_id:
        communities, err =  get_admin_communities(context)
        comm_ids = [c.id for c in communities] 
        users = [cm.user for cm in CommunityMember.objects.filter(community_id__in=comm_ids, user__is_deleted=False)]

        #now remove all duplicates
        users = remove_dups(users)

        return users, None
      elif not community:
        return [], None

      users = [cm.user for cm in CommunityMember.objects.filter(community=community, is_deleted=False, user__is_deleted=False)]
      users = remove_dups(users)
      return users, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_users_for_super_admin(self, context: Context):
    try:
      if not context.user_is_super_admin:
        return None, NotAuthorizedError()
      users = UserProfile.objects.filter(is_deleted=False)
      return users, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))


  def add_action_todo(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      user = get_user_or_die(context, args)
      action_id = args.get("action_id", None)
      household_id = args.get("household_id", None)
      vendor_id = args.get("vendor_id", None)
    
      if not user:
        return None, CustomMassenergizeError("sign_in_required / provide user_id or user_email")

      action: Action = Action.objects.get(id=action_id)
      if not action:
        return None, CustomMassenergizeError("Please provide a valid action_id")

      if household_id:
        household: RealEstateUnit = RealEstateUnit.objects.get(id=household_id)
      else:
        household = user.real_estate_units.all().first()

      if not household:
        household = RealEstateUnit(name=f"{user.preferred_name}'s Home'")
        household.save()
        user.real_estate_units.add(household)

      if vendor_id:
        vendor = Vendor.objects.get(id=vendor_id) #not required

      #if this already exists as a todo just move it over
      completed = UserActionRel.objects.filter(user=user, real_estate_unit=household, action=action)
      if completed:
        #TODO: update action stats
        completed.update(status="TODO")
        return completed.first(), None
      
      # create a new one since we didn't find it existed before
      new_user_action_rel = UserActionRel(user=user, action=action, real_estate_unit=household, status="TODO")

      if vendor_id:
        new_user_action_rel.vendor = vendor
      
      new_user_action_rel.save()

      return new_user_action_rel, None
    except Exception as e:
      capture_message(str(e), level="error")
      import traceback
      traceback.print_exc()
      return None, CustomMassenergizeError(str(e))

  def add_action_completed(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      user_id = context.user_id or args.get('user_id')
      user_email = context.user_email or args.get('user_email')
      action_id = args.get("action_id", None)
      household_id = args.get("household_id", None)
      vendor_id = args.get("vendor_id", None)

      user = None
      if user_id:
        user = UserProfile.objects.get(id=user_id)
      elif user_email:
        user = UserProfile.objects.get(email=user_email)

      if not user:
        return None, CustomMassenergizeError("sign_in_required / Provide user_id")

      action = Action.objects.get(id=action_id)
      if not action:
        return None, CustomMassenergizeError("Please provide an action_id")

      household = RealEstateUnit.objects.get(id=household_id)
      if not household:
        return None, CustomMassenergizeError("Please provide a household_id")


      # update all data points
      for t in action.tags.all():
        data = Data.objects.filter(community=action.community, tag=t)
        if data:
          data.update(value=F("value") + 1)

        else:
          #data for this community, action does not exist so create one
          d = Data(tag=t, community=action.community, value=1, name=f"{t.name}")
          d.save()
      

      #if this already exists as a todo just move it over
      completed = UserActionRel.objects.filter(user=user, real_estate_unit=household, action=action)
      if completed:
        completed.update(status="DONE")
        return completed.first(), None

      # create a new one since we didn't find it existed before
      new_user_action_rel = UserActionRel(user=user, action=action, real_estate_unit=household, status="DONE")

      if vendor_id:
        vendor = Vendor.objects.get(id=vendor_id) #not required
        new_user_action_rel.vendor = vendor

      new_user_action_rel.save()

      return new_user_action_rel, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))


  def list_todo_actions(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:

      if not context.user_is_logged_in:
        return [], CustomMassenergizeError("sign_in_required")
      
      user = get_user_or_die(context, args)
      household_id = args.get("household_id", None)

      if household_id:
        todo = UserActionRel.objects.filter(status="TODO", user=user, real_state_unit__id=household_id) 
      else:
        todo = UserActionRel.objects.filter(status="TODO", user=user) 

      return todo, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))


  def list_completed_actions(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:

      if not context.user_is_logged_in:
        return [], CustomMassenergizeError("sign_in_required")
      
      user = get_user_or_die(context, args)
      household_id = args.get("household_id", None)

      if household_id:
        todo = UserActionRel.objects.filter(status="DONE", user=user, real_state_unit__id=household_id) 
      else:
        todo = UserActionRel.objects.filter(status="DONE", user=user) 
      
      return todo, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))


  def remove_user_action(self, context: Context, user_action_id) -> (dict, MassEnergizeAPIError):
    try:
      if not context.user_is_logged_in:
        return [], CustomMassenergizeError("sign_in_required")
      
      user_action = UserActionRel.objects.get(pk=user_action_id)
      result = user_action.delete() 
      
      return result, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
