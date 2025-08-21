from utils import generate_id

# Ontology - Classes
class Classes: 

    activity = "crm:E7"
    production = "crm:E12"
    person = "crm:E21"
    physical_human_made_thing = "crm:E24"
    linguistic_object = "crm:E33"
    actor = "crm:E39"
    identifier = "crm:E42"
    time_span = "crm:E52"
    language = "crm:E56"
    
    activity_type = "crm-sup:C3"
    numeric_dimension = "crm-sup:C11"
    monetary_amount = "crm-sup:C21"
    currency = "crm-sup:C22"
    identifier_type = "crm-sup:C24"
    
    physical_human_made_thing_type = "sdh:C4"
    geographical_place = "sdh:C13"
    epistemic_location_of_a_physical_thing = "sdh:C15"
    epistemic_location_type = "sdh:C16"
    entity_quality_type = "sdh:C20"
    quantifiable_quality = "sdh:C28"
    intentional_expression = "sdh:C46"
    intentional_expression_type = "sdh:C47"
    physical_set = "sdh:C52"
    general_technique = "sdh:C53"
    quantifiable_quality_of_a_spatio_temporal_phenomenon = "sdh:C57"
    quantifiable_quality_of_an_intentional_event = "sdh:C71"
    quantifiable_quality_of_an_intentional_event_type = "sdh:C72"
    
    actor_social_quality = "sdh-slc:C2"
    occupation_teen = "sdh-slc:C8"
    occupation_peit = "sdh-slc:C9"
    holding_a_right_or_obligation = "sdh-slc:C14"
    participation = "sdh-slc:C15"
    economic_transaction = "sdh-slc:C37"
    presence_of_a_thing = "sdh-slc:C38"
    presence_of_a_thing_type = "sdh-slc:C44"

    mentioning = "geov:C28"

    expression = "frbroo:F2"

classes = Classes()

# Ontology - Properties
class Properties:
    type = "rdf:type"
    label = "rdfs:label"
    comment = "rdfs:comment"
    same_as = "owl:sameAs"

    is_identified_by = "crm:P1"
    has_note = "crm:P3"
    has_time_span = "crm:P4"
    occured_in_the_presence_of = "crm:P12"
    carried_out_by = "crm:P14"
    has_language = "crm:P72"
    begin_of_the_begin = "crm:P82a"
    end_of_the_end = "crm:P82b"
    has_value = "crm:P90"
    has_produced = "crm:P108"
    carries = "crm:P128"
    is_about = "crm:P129"
    has_symbolic_content = "crm:P190"

    has_activity_type = "crm-sup:P9"
    has_currency = "crm-sup:P16"
    has_identifier_type = "crm-sup:P19"
    same_as_external_identifier = "crm-sup:P20"

    is_part_of = "sdh:P5"
    took_place_at = "sdh:P6"
    is_localized_at = "sdh:P15"
    is_location_of = "sdh:P17"
    has_location_type = "sdh:P19"
    has_quantifiable_quality = "sdh:P22"
    has_quality_type = "sdh:P23"
    has_quality_dimension = "sdh:P35"
    has_setting = "sdh:P43"
    has_intentional_expression_identifing_type = "sdh:P48"
    is_quantifiable_quality_of = "sdh:P89"
    has_quantifiable_quality_of_and_intentional_event_type = "sdh:P90"

    was_or_is_composed_of_object_of_type = "sdh:P66"

    is_occupation_of = "sdh-slc:P4"
    is_about = "sdh-slc:P5"
    is_subjection_of = "sdh-slc:P8"
    is_right_of = "sdh-slc:P9"
    is_participation_of = "sdh-slc:P10"
    is_participation_in = "sdh-slc:P11"
    is_participation_in_the_quality_of = "sdh-slc:P12"
    is_presence_of = "sdh-slc:P75"
    is_presence_in = "sdh-slc:P76"
    has_type_of_presence = "sdh-slc:P77"

    mentions = "geov:P26"
    is_mentioned_in = "geov:P27"

    was_or_is_composed_of_objects_produced_with = "sdh-act:P20"




properties = Properties()


# Contants
class Contants:
    language_french = f'root:{generate_id()}'
    entityQualityType_number = f'root:{generate_id()}'
    currency_franc = f'root:{generate_id()}'
    currency_lires = f'root:{generate_id()}'
    identifierType_lugt = f'root:{generate_id()}'
    identifierType_url = f'root:{generate_id()}'
    epistemicLocationType_residence = f'root:{generate_id()}'
    epistemicLocationType_distributionPlace = f'root:{generate_id()}'
    entityQualityType_pageNumber = f'root:{generate_id()}'
    entityQualityType_lotNumber = f'root:{generate_id()}'
    quantiQualSpati_fees = f'root:{generate_id()}'
    actorSocialQuality_auctioneer = f'root:{generate_id()}'
    actorSocialQuality_expert = f'root:{generate_id()}'
    actorSocialQuality_seller = f'root:{generate_id()}'
    actorSocialQuality_buyer = f'root:{generate_id()}'
    activityType_auction = f'root:{generate_id()}'
    quantiQualIntEventType_hammerPrice = f'root:{generate_id()}'

constants = Contants()
