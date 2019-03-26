from typing import List

from pad_etl.processor.enemy_skillset import ESAction
from pad_etl.processor.enemy_skillset_processor import ProcessedSkillset, StandardSkillGroup, Moveset
from .enemy_skillset import *


def simple_dump_obj(o):
    def fmt_cond(c):
        msg = 'Condition: {} (ai:{} rnd:{})'.format(c.description, c._ai, c._rnd)
        if c.one_time:
            msg += ' (one-time: {})'.format(c.one_time)
        return msg

    def fmt_action_name(a):
        return '{}({}:{}) -> {}'.format(type(a).__name__, a.type, a.enemy_skill_id, a.name)

    if isinstance(o, ESSkillSet):
        msg = 'SkillSet:'
        if o.condition.description:
            msg += '\n\t{}'.format(fmt_cond(o.condition))
        for idx, behavior in enumerate(o.skill_list):
            msg += '\n\t[{}] {}'.format(idx, fmt_action_name(behavior))
            msg += '\n\t{}'.format(behavior.description)
        return msg
    else:
        msg = fmt_action_name(o)
        if hasattr(o, 'condition') and o.condition.description:
            msg += '\n\t{}'.format(fmt_cond(o.condition))
        msg += '\n{}'.format(o.description)
        return msg


def extract_used_skills(skillset: ProcessedSkillset, include_preemptive=True) -> List[ESAction]:
    """Flattens a ProcessedSkillset to a list of actions"""
    results = []

    if include_preemptive:
        results.extend(skillset.preemptives)

    def sg_extract(l: List[StandardSkillGroup]) -> List[ESAction]:
        return [item for sublist in l for item in sublist.skills]

    def moveset_extract(moveset: Moveset) -> List[ESAction]:
        moveset_results = []

        for hp_action in moveset.hp_actions:
            results.extend(sg_extract(hp_action.timed))
            results.extend(sg_extract(hp_action.repeating))

        if moveset.status_action:
            moveset_results.append(moveset.status_action)
        if moveset.dispel_action:
            moveset_results.append(moveset.dispel_action)

        return moveset_results

    results.extend(moveset_extract(skillset.moveset))
    for e_moveset in skillset.enemy_remaining_movesets:
        results.extend(moveset_extract(e_moveset))

    return results
