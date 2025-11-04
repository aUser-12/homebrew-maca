class Maca < Formula
  include Language::Python::Virtualenv

  desc "A feature complete mac address changer for macOS"
  homepage "https://github.com/aUser-12/homebrew-maca"
  url "https://github.com/aUser-12/homebrew-maca/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "<SHA256_SUM_OF_THE_TARBALL>"
  license "MIT"

  depends_on "python@3.11"

  def install
    bin.install "scripts/maca.py" => "maca"
  end

  test do
    system "#{bin}/maca", "--help"
  end
end
