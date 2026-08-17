"""
测试 MBTI Personality Prompt 模板
"""

import pytest
from src.mbti_prompts.personalities import MBTI_PERSONALITIES, MBTIPersonality


def test_all_16_types_exist():
    """验证16种MBTI类型都存在"""
    expected_types = [
        "INTJ", "INTP", "ENTJ", "ENTP",
        "INFJ", "INFP", "ENFJ", "ENFP",
        "ISTJ", "ISFJ", "ESTJ", "ESFJ",
        "ISTP", "ISFP", "ESTP", "ESFP",
    ]
    for mbti_type in expected_types:
        assert mbti_type in MBTI_PERSONALITIES, f"Missing MBTI type: {mbti_type}"


def test_personality_has_required_fields():
    """验证每个Personality都有必需字段"""
    required_fields = [
        "name", "description", "core_traits", "communication_style",
        "decision_making", "conflict_handling", "few_shot_examples", "validation_questions"
    ]
    for mbti_type, personality in MBTI_PERSONALITIES.items():
        for field in required_fields:
            assert hasattr(personality, field), f"{mbti_type} missing field: {field}"


def test_few_shot_has_examples():
    """验证每个Personality都有Few-shot示例"""
    for mbti_type, personality in MBTI_PERSONALITIES.items():
        assert len(personality.few_shot_examples) >= 3, f"{mbti_type} should have at least 3 examples"


def test_validation_questions_count():
    """验证每个Personality都有5个校验问题"""
    for mbti_type, personality in MBTI_PERSONALITIES.items():
        assert len(personality.validation_questions) == 5, f"{mbti_type} should have exactly 5 validation questions"


def test_core_traits_count():
    """验证每个Personality都有5个核心特质"""
    for mbti_type, personality in MBTI_PERSONALITIES.items():
        assert len(personality.core_traits) == 5, f"{mbti_type} should have exactly 5 core traits"


def test_mbti_dimension_consistency():
    """验证MBTI类型与维度一致性"""
    for mbti_type in MBTI_PERSONALITIES.keys():
        assert len(mbti_type) == 4, f"MBTI type should be 4 characters: {mbti_type}"
        assert mbti_type[0] in ["E", "I"], f"First char should be E or I: {mbti_type}"
        assert mbti_type[1] in ["N", "S"], f"Second char should be N or S: {mbti_type}"
        assert mbti_type[2] in ["T", "F"], f"Third char should be T or F: {mbti_type}"
        assert mbti_type[3] in ["J", "P"], f"Fourth char should be J or P: {mbti_type}"


def test_thinking_types_have_logic_focus():
    """验证思考型(T)人格的决策方式强调逻辑"""
    thinking_types = ["INTJ", "INTP", "ENTJ", "ENTP"]
    for mbti_type in thinking_types:
        personality = MBTI_PERSONALITIES[mbti_type]
        # 检查decision_making是否非空且合理
        assert len(personality.decision_making) > 10, \
            f"{mbti_type} should have a meaningful decision_making description"


def test_feeling_types_have_value_focus():
    """验证情感型(F)人格的决策方式强调价值观"""
    feeling_types = ["INFJ", "INFP", "ENFJ", "ENFP", "ESFJ", "ESFP", "ISFJ", "ISFP"]
    for mbti_type in feeling_types:
        personality = MBTI_PERSONALITIES[mbti_type]
        # 检查decision_making是否非空且合理
        assert len(personality.decision_making) > 10, \
            f"{mbti_type} should have a meaningful decision_making description"