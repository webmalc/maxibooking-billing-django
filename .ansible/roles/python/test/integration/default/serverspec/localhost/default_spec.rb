require 'spec_helper'

describe 'ansible-python::default' do

  describe package('python-dev') do
    it { should be_installed.by('apt') }
  end

  describe package('python-dev') do
    it { should be_installed.by('apt') }
  end

  describe package('python-setuptools') do
    it { should be_installed.by('apt') }
  end

  describe package('python-pip') do
    it { should be_installed.by('apt') }
  end

  describe package('python3') do
    it { should be_installed.by('apt') }
  end

  describe package('python3-dev') do
    it { should be_installed.by('apt') }
  end

  describe package('python3-setuptools') do
    it { should be_installed.by('apt') }
  end

  describe package('python3-pip') do
    it { should be_installed.by('apt') }
  end

end
