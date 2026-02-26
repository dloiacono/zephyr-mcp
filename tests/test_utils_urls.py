"""Tests for zephyr_mcp.utils.urls module."""

from zephyr_mcp.utils.urls import is_atlassian_cloud_url


class TestIsAtlassianCloudUrl:
    def test_none(self):
        assert is_atlassian_cloud_url(None) is False

    def test_empty_string(self):
        assert is_atlassian_cloud_url("") is False

    def test_atlassian_net(self):
        assert is_atlassian_cloud_url("https://mycompany.atlassian.net") is True

    def test_jira_com(self):
        assert is_atlassian_cloud_url("https://mycompany.jira.com") is True

    def test_jira_dev_com(self):
        assert is_atlassian_cloud_url("https://mycompany.jira-dev.com") is True

    def test_api_atlassian(self):
        assert is_atlassian_cloud_url("https://api.atlassian.com") is True

    def test_zephyrscale_smartbear(self):
        assert is_atlassian_cloud_url("https://api.zephyrscale.smartbear.com/v2") is True

    def test_atlassian_gov(self):
        assert is_atlassian_cloud_url("https://mycompany.atlassian-us-gov-mod.net") is True
        assert is_atlassian_cloud_url("https://mycompany.atlassian-us-gov.net") is True

    def test_localhost(self):
        assert is_atlassian_cloud_url("http://localhost:8080") is False

    def test_127_ip(self):
        assert is_atlassian_cloud_url("http://127.0.0.1:8080") is False

    def test_192_168_ip(self):
        assert is_atlassian_cloud_url("http://192.168.1.1") is False

    def test_10_ip(self):
        assert is_atlassian_cloud_url("http://10.0.0.1") is False

    def test_172_16_ip(self):
        assert is_atlassian_cloud_url("http://172.16.0.1") is False

    def test_172_31_ip(self):
        assert is_atlassian_cloud_url("http://172.31.255.1") is False

    def test_172_outside_range(self):
        assert is_atlassian_cloud_url("http://172.32.0.1") is not True or is_atlassian_cloud_url("http://172.32.0.1") is False

    def test_custom_server(self):
        assert is_atlassian_cloud_url("https://jira.mycompany.com") is False

    def test_self_hosted(self):
        assert is_atlassian_cloud_url("https://jira.internal.corp") is False
