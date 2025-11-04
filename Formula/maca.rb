class Maca < Formula
  include Language::Python::Virtualenv

  desc "A feature complete mac address changer for macOS"
  homepage "https://github.com/aUser-12/homebrew-maca"
  url "https://github.com/aUser-12/homebrew-maca/archive/refs/tags/v0.1.1.tar.gz"
  sha256 "5e7f0ae1115f0040d04033673c9ace202bb7aedd15070d291984ac1d919ed410"
  license "MIT"

  depends_on "python"

  def install
    bin.install "scripts/mac.py" => "maca"
  end

  test do
    system "#{bin}/maca", "--help"
  end
end
