
from _main_.utils.common import serialize, serialize_all
from apps__campaigns.models import  CampaignCommunity, CampaignConfiguration, CampaignEvent, CampaignManager, CampaignPartner, CampaignTechnology, CampaignTechnologyLike, CampaignTechnologyTestimonial, CampaignTechnologyView, Comment, Technology, TechnologyCoach, TechnologyOverview, TechnologyVendor
from database.utils.common import get_json_if_not_none


BASE_NAVIGATION = [
  { "key": "home", "url": "/", "text": "Home", "icon": "fa-home" },
  {
    "key": "questions",
    "url": "#testimonial-section",
    "text": "Questions",
    "icon": "fa-question-circle",
  },
  {
    "key": "coaches",
    "url": "#coaches-section",
    "text": "Coaches",
    "icon": "fa-users",
    "children":[],
  },

  {
    "key": "vendors",
    "url": "#",
    "text": "Vendors",
    "children":[],
    "icon": "fa-sell",
  },
  {
    "key": "incentives",
    "url": "#",
    "text": "Incentives",
    "children":[],
    "icon": "fa-money",
  },
  {
    "key": "events",
    "url": "#",
    "text": "Events",
    "children":[],
    "icon": "fa-calendar",
  },
  {
    "key": "testimonial",
    "url": "#",
    "text": "Testimonial",
    "children":[],
    "icon": "fa-comment",
  },
  {
    "key": "contact-us",
    "url": "#",
    "text": "Contact Us",
    "icon": "fa-phone",
  },
];


def get_campaign_details(campaign_id, for_campaign=False):
    techs = CampaignTechnology.objects.filter(campaign__id=campaign_id, is_deleted=False)
    ser_techs = serialize_all(techs, full=True)
    prepared = [{"campaign_technology_id":x.get("id"),**get_campaign_technology_details(x.get("id"), for_campaign)} for x in ser_techs]
    managers = CampaignManager.objects.filter(campaign_id=campaign_id, is_deleted=False)
    partners = CampaignPartner.objects.filter(campaign_id=campaign_id, is_deleted=False)
    communities = CampaignCommunity.objects.filter(campaign_id=campaign_id, is_deleted=False)
    config = CampaignConfiguration.objects.filter(campaign__id=campaign_id, is_deleted=False).first()
    key_contact = CampaignManager.objects.filter(campaign__id=campaign_id, is_deleted=False, is_key_contact=True).first()

    return {
        "key_contact": {
            "name": key_contact.user.full_name,
            "email": key_contact.user.email,
            "phone_number": key_contact.contact,
            "image": get_json_if_not_none(key_contact.user.profile_picture),
        } if key_contact else None,
        
        "technologies": prepared,
        "communities": serialize_all(communities),
        "managers": serialize_all(managers),
        "partners": serialize_all(partners),
        "config": serialize(config),
        "navigation": generate_campaign_navigation(campaign_id),
    }


def get_campaign_technology_details(campaign_technology_id, campaign_home, email=None):
    campaign_tech = CampaignTechnology.objects.filter(id=campaign_technology_id).first()
    events = CampaignEvent.objects.filter(event__technology__id=campaign_tech.technology.id, is_deleted=False)
    testimonials = CampaignTechnologyTestimonial.objects.filter(is_deleted=False,campaign_technology__id=campaign_technology_id)
    tech_data = get_technology_details(campaign_tech.technology.id)

    if campaign_home:
        return {
            "testimonials":serialize_all(testimonials[:3]),
            "events": serialize_all(events[:3], full=True),
            "coaches": tech_data.get("coaches", [])[:3],
            "campaign_id": campaign_tech.campaign.id,
            **campaign_tech.technology.simple_json()
        }
    views = CampaignTechnologyView.objects.filter(campaign_technology__id=campaign_technology_id, is_deleted=False)
    likes = CampaignTechnologyLike.objects.filter(campaign_technology__id=campaign_technology_id, is_deleted=False)
    liked = CampaignTechnologyLike.objects.filter(campaign_technology__id=campaign_technology_id, is_deleted=False, user__email=email).exists()
    comments = Comment.objects.filter(campaign_technology__id=campaign_technology_id, is_deleted=False)

    return {
            **get_technology_details(campaign_tech.technology.id),
            "views":views.count(),
            "has_liked":liked,
            "likes":likes.count(),
            "testimonials":serialize_all(testimonials),
            "comments": serialize_all(comments),
            "events": serialize_all(events, full=True),
            "campaign_id": campaign_tech.campaign.id,
        }



def get_technology_details(technology_id):
    tech = Technology.objects.filter(id=technology_id).first()
    coaches = TechnologyCoach.objects.filter(technology_id=technology_id, is_deleted=False)
    incentives = TechnologyOverview.objects.filter(technology_id=technology_id, is_deleted=False)
    vendors = TechnologyVendor.objects.filter(technology_id=technology_id, is_deleted=False)

    return {
            "coaches": serialize_all(coaches),
            "overview": serialize_all(incentives),
            "vendors": serialize_all(vendors),
            **serialize(tech)
        }
def generate_campaign_navigation(campaign_id):
    campaign_techs = CampaignTechnology.objects.filter(campaign__id=campaign_id, is_deleted=False)
    BASE_NAVIGATION[0]["url"] = f"/{campaign_id}"

    for tech in campaign_techs:
        tech_details = get_technology_details(tech.technology.id)
        if tech_details.get("coaches"):
            BASE_NAVIGATION[2]["children"].append({"key":tech.id, "url":f"/campaign/{campaign_id}/technology/{tech.id}", "text":tech.technology.name})
        if tech_details.get("vendors"):
            BASE_NAVIGATION[3]["children"].append({"key":tech.id, "url":f"/campaign/{campaign_id}/technology/{tech.id}", "text":tech.technology.name})
        if tech_details.get("overview"):
            BASE_NAVIGATION[4]["children"].append({"key":tech.id, "url":f"/campaign/{campaign_id}/technology/{tech.id}", "text":tech.technology.name})
        if tech_details.get("testimonials"):
            BASE_NAVIGATION[5]["children"].append({"key":tech.id, "url":f"/campaign/{campaign_id}/technology/{tech.id}", "text":tech.technology.name})
        if tech_details.get("events"):
            BASE_NAVIGATION[6]["children"].append({"key":tech.id, "url":f"/campaign/{campaign_id}/technology/{tech.id}", "text":tech.technology.name})
    return BASE_NAVIGATION