class Maca < Formula
  include Language::Python::Virtualenv

  desc "A feature complete mac address changer for macOS"
  homepage "https://github.com/aUser-12/homebrew-maca"
  url "https://github.com/aUser-12/homebrew-maca/archive/refs/tags/v0.1.2.tar.gz"
  sha256 "9cd3eba88e81e101be8fcb2fd7e1a4c8f436c54e3b0b79a1f54d87bc82809a28"
  license "MIT"

  depends_on "python"

  def install
    bin.install "scripts/mac.py" => "maca"
  end

  test do
    system "#{bin}/maca", "--help"
  end
end
